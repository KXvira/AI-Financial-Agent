"""
M-Pesa integration module for handling payment workflows
"""
import requests
import base64
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel

# Import database service
try:
    from database.mongodb import Database
    db_available = True
except ImportError:
    db_available = False
    print("Database module not available. Using mock data only.")

# Import reconciliation service
try:
    from reconciliation.service import ReconciliationService
    reconciliation_available = True
except ImportError:
    reconciliation_available = False
    print("Reconciliation module not available. Reconciliation features disabled.")

logger = logging.getLogger("financial-agent.mpesa")

class MpesaConfig:
    """M-Pesa API configuration"""
    
    def __init__(self):
        # In production, load these from secure environment variables or vault
        self.consumer_key = os.environ.get("MPESA_CONSUMER_KEY", "your-consumer-key")
        self.consumer_secret = os.environ.get("MPESA_CONSUMER_SECRET", "your-consumer-secret")
        self.business_shortcode = os.environ.get("MPESA_SHORTCODE", "174379")  # Default is sandbox
        self.pass_key = os.environ.get("MPESA_PASS_KEY", "your-passkey")
        self.env = os.environ.get("MPESA_ENV", "sandbox")  # or "production"
        
        # API URLs depending on environment
        if self.env == "production":
            self.base_url = "https://api.safaricom.co.ke"
        else:
            self.base_url = "https://sandbox.safaricom.co.ke"
        
        # API endpoints
        self.token_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        self.stk_push_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        self.query_url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
        
        # Callbacks
        self.callback_url = os.environ.get(
            "MPESA_CALLBACK_URL", 
            "https://your-domain.com/api/mpesa/callback"
        )


class MpesaService:
    """Service for handling M-Pesa payment operations"""
    
    def __init__(self):
        self.config = MpesaConfig()
        self.access_token = None
        self.token_expiry = datetime.now()
        
        # Initialize database connection if available
        if db_available:
            self.db = Database.get_instance()
        else:
            self.db = None
            
        # Initialize reconciliation service if available
        if reconciliation_available:
            self.reconciliation_service = ReconciliationService()
        else:
            self.reconciliation_service = None
    
    async def get_access_token(self) -> str:
        """Get OAuth access token from Safaricom"""
        try:
            # Create auth string and encode it
            auth_string = f"{self.config.consumer_key}:{self.config.consumer_secret}"
            auth_bytes = auth_string.encode("ascii")
            encoded_auth = base64.b64encode(auth_bytes).decode("ascii")
            
            headers = {
                "Authorization": f"Basic {encoded_auth}"
            }
            
            # Make request to get token
            response = requests.get(self.config.token_url, headers=headers)
            response_data = response.json()
            
            if "access_token" in response_data:
                self.access_token = response_data["access_token"]
                return self.access_token
            else:
                logger.error(f"Failed to get access token: {response_data}")
                raise Exception("Failed to get M-Pesa access token")
                
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            raise
    
    async def initiate_stk_push(self, 
                           phone_number: str, 
                           amount: float, 
                           reference: str, 
                           description: str) -> Dict[str, Any]:
        """
        Initiate STK Push payment request to customer's phone
        
        Args:
            phone_number: Customer phone number (format: 254XXXXXXXXX)
            amount: Payment amount
            reference: Payment reference (e.g., invoice number)
            description: Payment description
            
        Returns:
            Dict with payment request result
        """
        try:
            # Ensure phone number is in correct format (254XXXXXXXXX)
            if phone_number.startswith("+"):
                phone_number = phone_number[1:]
            if phone_number.startswith("0"):
                phone_number = "254" + phone_number[1:]
                
            # Get access token if we don't have one
            if not self.access_token:
                await self.get_access_token()
            
            # Generate password
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            password_string = f"{self.config.business_shortcode}{self.config.pass_key}{timestamp}"
            password_bytes = password_string.encode("ascii")
            encoded_password = base64.b64encode(password_bytes).decode("ascii")
            
            # Prepare request payload
            payload = {
                "BusinessShortCode": self.config.business_shortcode,
                "Password": encoded_password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),  # Must be integer
                "PartyA": phone_number,
                "PartyB": self.config.business_shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": self.config.callback_url,
                "AccountReference": reference[:20],  # Limit to 20 chars
                "TransactionDesc": description[:13]  # Limit to 13 chars
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Make STK push request
            response = requests.post(
                self.config.stk_push_url,
                json=payload,
                headers=headers
            )
            
            result = response.json()
            
            # Log the transaction
            logger.info(f"STK Push initiated for {phone_number}, amount: {amount}, ref: {reference}")
            logger.debug(f"STK Push response: {json.dumps(result)}")
            
            # Store transaction in database for reconciliation
            if self.db is not None:
                transaction_data = {
                    "reference": reference,
                    "gateway": "mpesa",
                    "amount": float(amount),
                    "phone_number": phone_number,
                    "status": "initiated",
                    "gateway_data": result,
                    "request_timestamp": datetime.now(),
                    "metadata": {
                        "description": description,
                        "checkout_request_id": result.get("CheckoutRequestID", ""),
                        "merchant_request_id": result.get("MerchantRequestID", "")
                    }
                }
                
                await self.db.store_transaction(transaction_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error initiating STK Push: {str(e)}")
            raise

    async def check_transaction_status(self, checkout_request_id: str) -> Dict[str, Any]:
        """
        Check the status of an STK push transaction
        
        Args:
            checkout_request_id: The CheckoutRequestID from the STK push request
            
        Returns:
            Dict with transaction status details
        """
        try:
            # Get access token if we don't have one
            if not self.access_token:
                await self.get_access_token()
                
            # Generate password
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            password_string = f"{self.config.business_shortcode}{self.config.pass_key}{timestamp}"
            password_bytes = password_string.encode("ascii")
            encoded_password = base64.b64encode(password_bytes).decode("ascii")
            
            payload = {
                "BusinessShortCode": self.config.business_shortcode,
                "Password": encoded_password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.config.query_url,
                json=payload,
                headers=headers
            )
            
            result = response.json()
            
            logger.info(f"Transaction status query for {checkout_request_id}: {result.get('ResultDesc', 'No result')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking transaction status: {str(e)}")
            raise

    async def process_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process M-Pesa callback data
        
        Args:
            callback_data: The callback data from M-Pesa
            
        Returns:
            Dict with processing result
        """
        try:
            logger.info(f"Processing M-Pesa callback: {json.dumps(callback_data)}")
            
            # Extract key information
            result_code = callback_data.get("Body", {}).get("stkCallback", {}).get("ResultCode")
            
            if result_code == 0:
                # Payment successful
                callback_metadata = callback_data.get("Body", {}).get("stkCallback", {}).get("CallbackMetadata", {}).get("Item", [])
                
                # Extract payment details from metadata
                payment_details = {}
                for item in callback_metadata:
                    if item.get("Name") == "Amount":
                        payment_details["amount"] = item.get("Value")
                    elif item.get("Name") == "MpesaReceiptNumber":
                        payment_details["receipt_number"] = item.get("Value")
                    elif item.get("Name") == "TransactionDate":
                        payment_details["transaction_date"] = item.get("Value")
                    elif item.get("Name") == "PhoneNumber":
                        payment_details["phone_number"] = item.get("Value")
                
                # Get checkout request ID for finding the transaction
                checkout_request_id = callback_data.get("Body", {}).get("stkCallback", {}).get("CheckoutRequestID")
                
                # Store successful transaction in database
                if self.db is not None:
                    # First find the transaction by checkout request ID
                    transactions = await self.db.transactions.find(
                        {"metadata.checkout_request_id": checkout_request_id}
                    ).to_list(length=1)
                    
                    if transactions:
                        transaction = transactions[0]
                        transaction_id = transaction.get("_id")
                        
                        # Update transaction with payment details
                        update_data = {
                            "status": "completed",
                            "gateway_reference": payment_details.get("receipt_number"),
                            "completion_timestamp": datetime.now(),
                            "gateway_data": {
                                **transaction.get("gateway_data", {}),
                                "callback": callback_data,
                                "payment_details": payment_details
                            }
                        }
                        
                        await self.db.update_transaction(transaction_id, update_data)
                        
                        # Send to reconciliation service if available
                        if self.reconciliation_service is not None:
                            # Create reconciliation payment data
                            reconciliation_data = {
                                "transaction_id": transaction_id,
                                "receipt_number": payment_details.get("receipt_number"),
                                "phone_number": payment_details.get("phone_number"),
                                "amount": payment_details.get("amount"),
                                "transaction_date": payment_details.get("transaction_date"),
                                "reference": transaction.get("reference")
                            }
                            
                            # Queue for reconciliation
                            await self.reconciliation_service.queue_for_reconciliation(reconciliation_data)
                
                return {
                    "status": "success",
                    "message": "Payment successful",
                    "details": payment_details
                }
                
            else:
                # Payment failed
                result_desc = callback_data.get("Body", {}).get("stkCallback", {}).get("ResultDesc", "Unknown error")
                checkout_request_id = callback_data.get("Body", {}).get("stkCallback", {}).get("CheckoutRequestID")
                
                # Update transaction status in database
                if self.db is not None:
                    # First find the transaction by checkout request ID
                    transactions = await self.db.transactions.find(
                        {"metadata.checkout_request_id": checkout_request_id}
                    ).to_list(length=1)
                    
                    if transactions:
                        transaction = transactions[0]
                        transaction_id = transaction.get("_id")
                        
                        # Update transaction with failure details
                        update_data = {
                            "status": "failed",
                            "completion_timestamp": datetime.now(),
                            "gateway_data": {
                                **transaction.get("gateway_data", {}),
                                "callback": callback_data,
                                "error": {
                                    "code": result_code,
                                    "description": result_desc
                                }
                            }
                        }
                        
                        await self.db.update_transaction(transaction_id, update_data)
                
                return {
                    "status": "failed",
                    "message": "Payment failed",
                    "details": {
                        "result_code": result_code,
                        "result_desc": result_desc
                    }
                }
                
        except Exception as e:
            logger.error(f"Error processing callback: {str(e)}")
            raise
