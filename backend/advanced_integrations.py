"""
Sprint 8: Advanced Banking & Financial Integrations
Real-time banking APIs, accounting software, and market data providers
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
import hashlib
import hmac
import base64
from decimal import Decimal
import xml.etree.ElementTree as ET

class BankingProvider(Enum):
    """Supported banking providers"""
    PLAID = "plaid"
    YODLEE = "yodlee"
    OPEN_BANKING_UK = "open_banking_uk"
    PSD2_EU = "psd2_eu"
    MPESA = "mpesa"
    FLUTTERWAVE = "flutterwave"

class AccountingProvider(Enum):
    """Supported accounting software providers"""
    QUICKBOOKS = "quickbooks"
    XERO = "xero"
    SAGE = "sage"
    FRESHBOOKS = "freshbooks"
    WAVE = "wave"

class MarketDataProvider(Enum):
    """Supported market data providers"""
    ALPHA_VANTAGE = "alpha_vantage"
    YAHOO_FINANCE = "yahoo_finance"
    IEX_CLOUD = "iex_cloud"
    BLOOMBERG = "bloomberg"
    FOREX_API = "forex_api"

class TransactionType(Enum):
    """Transaction types"""
    DEBIT = "debit"
    CREDIT = "credit"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    REFUND = "refund"

@dataclass
class BankAccount:
    """Bank account information"""
    account_id: str
    provider: str
    account_number: str
    account_name: str
    account_type: str
    balance: Decimal
    currency: str
    last_updated: datetime
    is_active: bool = True

@dataclass
class Transaction:
    """Financial transaction"""
    transaction_id: str
    account_id: str
    amount: Decimal
    currency: str
    transaction_type: TransactionType
    description: str
    merchant_name: Optional[str]
    category: Optional[str]
    date: datetime
    reference: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MarketData:
    """Market data point"""
    symbol: str
    provider: str
    price: Decimal
    currency: str
    timestamp: datetime
    volume: Optional[int] = None
    change: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None

class BankingIntegration:
    """
    Banking API integration manager
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.providers: Dict[str, Dict[str, Any]] = {}
        self.accounts: Dict[str, BankAccount] = {}
        self.transactions: List[Transaction] = []
        
        # Initialize provider configurations
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize banking provider configurations"""
        self.providers = {
            BankingProvider.PLAID.value: {
                "base_url": "https://production.plaid.com",
                "auth_type": "api_key",
                "endpoints": {
                    "accounts": "/accounts/get",
                    "transactions": "/transactions/get",
                    "balance": "/accounts/balance/get",
                    "identity": "/identity/get"
                }
            },
            BankingProvider.MPESA.value: {
                "base_url": "https://api.safaricom.co.ke",
                "auth_type": "oauth2",
                "endpoints": {
                    "balance": "/mpesa/accountbalance/v1/query",
                    "transaction_status": "/mpesa/transactionstatus/v1/query",
                    "b2c": "/mpesa/b2c/v1/paymentrequest",
                    "c2b": "/mpesa/c2b/v1/registerurl"
                }
            },
            BankingProvider.OPEN_BANKING_UK.value: {
                "base_url": "https://api.openbanking.org.uk",
                "auth_type": "oauth2",
                "endpoints": {
                    "accounts": "/open-banking/v3.1/aisp/accounts",
                    "transactions": "/open-banking/v3.1/aisp/accounts/{account_id}/transactions",
                    "balance": "/open-banking/v3.1/aisp/accounts/{account_id}/balances"
                }
            }
        }

    async def connect_bank_account(self, provider: BankingProvider, 
                                 credentials: Dict[str, Any],
                                 tenant_id: str) -> Dict[str, Any]:
        """Connect to bank account via API"""
        try:
            provider_config = self.providers.get(provider.value)
            if not provider_config:
                raise ValueError(f"Unsupported provider: {provider.value}")
            
            # Authenticate with provider
            auth_token = await self._authenticate_provider(provider, credentials)
            
            # Fetch account information
            accounts = await self._fetch_accounts(provider, auth_token)
            
            # Store account information
            for account_data in accounts:
                account = BankAccount(
                    account_id=f"{provider.value}_{account_data['id']}",
                    provider=provider.value,
                    account_number=account_data.get('account_number', '****'),
                    account_name=account_data.get('name', 'Unknown'),
                    account_type=account_data.get('type', 'checking'),
                    balance=Decimal(str(account_data.get('balance', 0))),
                    currency=account_data.get('currency', 'USD'),
                    last_updated=datetime.now()
                )
                
                self.accounts[account.account_id] = account
            
            return {
                "status": "connected",
                "provider": provider.value,
                "accounts_connected": len(accounts),
                "accounts": [
                    {
                        "account_id": acc.account_id,
                        "account_name": acc.account_name,
                        "account_type": acc.account_type,
                        "balance": float(acc.balance),
                        "currency": acc.currency
                    }
                    for acc in [self.accounts[f"{provider.value}_{acc['id']}"] for acc in accounts]
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Bank account connection failed: {str(e)}")
            raise

    async def _authenticate_provider(self, provider: BankingProvider, 
                                   credentials: Dict[str, Any]) -> str:
        """Authenticate with banking provider"""
        provider_config = self.providers[provider.value]
        
        if provider.value == BankingProvider.PLAID.value:
            return await self._authenticate_plaid(credentials)
        elif provider.value == BankingProvider.MPESA.value:
            return await self._authenticate_mpesa(credentials)
        elif provider.value == BankingProvider.OPEN_BANKING_UK.value:
            return await self._authenticate_open_banking_uk(credentials)
        else:
            raise ValueError(f"Authentication not implemented for {provider.value}")

    async def _authenticate_plaid(self, credentials: Dict[str, Any]) -> str:
        """Authenticate with Plaid"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "client_id": credentials["client_id"],
                "secret": credentials["secret"],
                "access_token": credentials["access_token"]
            }
            
            async with session.post(
                f"{self.providers[BankingProvider.PLAID.value]['base_url']}/accounts/get",
                json=payload
            ) as response:
                if response.status == 200:
                    return credentials["access_token"]
                else:
                    raise ValueError("Plaid authentication failed")

    async def _authenticate_mpesa(self, credentials: Dict[str, Any]) -> str:
        """Authenticate with M-Pesa"""
        async with aiohttp.ClientSession() as session:
            # Generate OAuth token
            auth_string = base64.b64encode(
                f"{credentials['consumer_key']}:{credentials['consumer_secret']}".encode()
            ).decode()
            
            headers = {
                "Authorization": f"Basic {auth_string}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            async with session.get(
                f"{self.providers[BankingProvider.MPESA.value]['base_url']}/oauth/v1/generate?grant_type=client_credentials",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["access_token"]
                else:
                    raise ValueError("M-Pesa authentication failed")

    async def _authenticate_open_banking_uk(self, credentials: Dict[str, Any]) -> str:
        """Authenticate with Open Banking UK"""
        # Simplified OAuth2 flow
        return credentials.get("access_token", "")

    async def _fetch_accounts(self, provider: BankingProvider, 
                            auth_token: str) -> List[Dict[str, Any]]:
        """Fetch accounts from provider"""
        provider_config = self.providers[provider.value]
        base_url = provider_config["base_url"]
        
        if provider.value == BankingProvider.PLAID.value:
            return await self._fetch_plaid_accounts(auth_token, base_url)
        elif provider.value == BankingProvider.MPESA.value:
            return await self._fetch_mpesa_accounts(auth_token, base_url)
        elif provider.value == BankingProvider.OPEN_BANKING_UK.value:
            return await self._fetch_open_banking_accounts(auth_token, base_url)
        else:
            return []

    async def _fetch_plaid_accounts(self, access_token: str, base_url: str) -> List[Dict[str, Any]]:
        """Fetch Plaid accounts"""
        async with aiohttp.ClientSession() as session:
            payload = {"access_token": access_token}
            
            async with session.post(f"{base_url}/accounts/get", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        {
                            "id": acc["account_id"],
                            "name": acc["name"],
                            "type": acc["type"],
                            "account_number": acc["mask"],
                            "balance": acc["balances"]["current"],
                            "currency": "USD"
                        }
                        for acc in data.get("accounts", [])
                    ]
                return []

    async def _fetch_mpesa_accounts(self, access_token: str, base_url: str) -> List[Dict[str, Any]]:
        """Fetch M-Pesa account balance"""
        # M-Pesa typically has one main account per business
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # This is a simplified example - actual implementation would vary
            return [
                {
                    "id": "mpesa_main",
                    "name": "M-Pesa Main Account",
                    "type": "mobile_money",
                    "account_number": "****",
                    "balance": 0,  # Would fetch actual balance
                    "currency": "KES"
                }
            ]

    async def _fetch_open_banking_accounts(self, access_token: str, base_url: str) -> List[Dict[str, Any]]:
        """Fetch Open Banking UK accounts"""
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            async with session.get(
                f"{base_url}/open-banking/v3.1/aisp/accounts",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        {
                            "id": acc["AccountId"],
                            "name": acc["Nickname"] or "Account",
                            "type": acc["AccountType"],
                            "account_number": acc["Account"][0]["Identification"],
                            "balance": 0,  # Would fetch from balance endpoint
                            "currency": acc["Currency"]
                        }
                        for acc in data.get("Data", {}).get("Account", [])
                    ]
                return []

    async def sync_transactions(self, account_id: str, days: int = 30) -> List[Transaction]:
        """Sync transactions for an account"""
        try:
            account = self.accounts.get(account_id)
            if not account:
                raise ValueError("Account not found")
            
            provider = BankingProvider(account.provider)
            
            # Fetch recent transactions
            transactions_data = await self._fetch_transactions(
                provider, account_id, days
            )
            
            # Convert to Transaction objects
            transactions = []
            for txn_data in transactions_data:
                transaction = Transaction(
                    transaction_id=txn_data["id"],
                    account_id=account_id,
                    amount=Decimal(str(txn_data["amount"])),
                    currency=txn_data.get("currency", account.currency),
                    transaction_type=TransactionType(txn_data.get("type", "debit")),
                    description=txn_data.get("description", ""),
                    merchant_name=txn_data.get("merchant"),
                    category=txn_data.get("category"),
                    date=datetime.fromisoformat(txn_data["date"]),
                    reference=txn_data.get("reference"),
                    metadata=txn_data.get("metadata", {})
                )
                transactions.append(transaction)
            
            # Store transactions
            self.transactions.extend(transactions)
            
            return transactions
            
        except Exception as e:
            self.logger.error(f"Transaction sync failed: {str(e)}")
            raise

    async def _fetch_transactions(self, provider: BankingProvider, 
                                account_id: str, days: int) -> List[Dict[str, Any]]:
        """Fetch transactions from provider"""
        # Implementation would vary by provider
        # This is a simplified example
        return []

class AccountingIntegration:
    """
    Accounting software integration manager
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connected_systems: Dict[str, Dict[str, Any]] = {}

    async def connect_accounting_system(self, provider: AccountingProvider,
                                      credentials: Dict[str, Any],
                                      tenant_id: str) -> Dict[str, Any]:
        """Connect to accounting system"""
        try:
            if provider == AccountingProvider.QUICKBOOKS:
                return await self._connect_quickbooks(credentials, tenant_id)
            elif provider == AccountingProvider.XERO:
                return await self._connect_xero(credentials, tenant_id)
            else:
                raise ValueError(f"Unsupported accounting provider: {provider.value}")
                
        except Exception as e:
            self.logger.error(f"Accounting system connection failed: {str(e)}")
            raise

    async def _connect_quickbooks(self, credentials: Dict[str, Any], 
                                tenant_id: str) -> Dict[str, Any]:
        """Connect to QuickBooks Online"""
        # Simplified QuickBooks integration
        connection_id = str(uuid.uuid4())
        
        self.connected_systems[connection_id] = {
            "provider": AccountingProvider.QUICKBOOKS.value,
            "tenant_id": tenant_id,
            "credentials": credentials,
            "connected_at": datetime.now(),
            "last_sync": None
        }
        
        return {
            "status": "connected",
            "connection_id": connection_id,
            "provider": AccountingProvider.QUICKBOOKS.value
        }

    async def _connect_xero(self, credentials: Dict[str, Any], 
                           tenant_id: str) -> Dict[str, Any]:
        """Connect to Xero"""
        # Simplified Xero integration
        connection_id = str(uuid.uuid4())
        
        self.connected_systems[connection_id] = {
            "provider": AccountingProvider.XERO.value,
            "tenant_id": tenant_id,
            "credentials": credentials,
            "connected_at": datetime.now(),
            "last_sync": None
        }
        
        return {
            "status": "connected",
            "connection_id": connection_id,
            "provider": AccountingProvider.XERO.value
        }

    async def sync_accounting_data(self, connection_id: str) -> Dict[str, Any]:
        """Sync data from accounting system"""
        try:
            connection = self.connected_systems.get(connection_id)
            if not connection:
                raise ValueError("Connection not found")
            
            provider = connection["provider"]
            
            if provider == AccountingProvider.QUICKBOOKS.value:
                return await self._sync_quickbooks_data(connection)
            elif provider == AccountingProvider.XERO.value:
                return await self._sync_xero_data(connection)
            else:
                raise ValueError(f"Sync not implemented for {provider}")
                
        except Exception as e:
            self.logger.error(f"Accounting data sync failed: {str(e)}")
            raise

    async def _sync_quickbooks_data(self, connection: Dict[str, Any]) -> Dict[str, Any]:
        """Sync QuickBooks data"""
        # Simplified sync implementation
        return {
            "invoices_synced": 0,
            "customers_synced": 0,
            "last_sync": datetime.now().isoformat()
        }

    async def _sync_xero_data(self, connection: Dict[str, Any]) -> Dict[str, Any]:
        """Sync Xero data"""
        # Simplified sync implementation
        return {
            "invoices_synced": 0,
            "contacts_synced": 0,
            "last_sync": datetime.now().isoformat()
        }

class MarketDataIntegration:
    """
    Market data provider integration
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.providers: Dict[str, Dict[str, Any]] = {}
        self.market_data: List[MarketData] = []
        
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize market data providers"""
        self.providers = {
            MarketDataProvider.ALPHA_VANTAGE.value: {
                "base_url": "https://www.alphavantage.co/query",
                "rate_limit": 5,  # requests per minute
                "endpoints": {
                    "quote": "GLOBAL_QUOTE",
                    "intraday": "TIME_SERIES_INTRADAY",
                    "forex": "FX_INTRADAY"
                }
            },
            MarketDataProvider.YAHOO_FINANCE.value: {
                "base_url": "https://query1.finance.yahoo.com/v8/finance/chart",
                "rate_limit": 2000,  # requests per hour
                "endpoints": {
                    "quote": "{symbol}",
                    "history": "{symbol}?period1={start}&period2={end}"
                }
            }
        }

    async def get_stock_price(self, symbol: str, 
                            provider: MarketDataProvider = MarketDataProvider.ALPHA_VANTAGE) -> MarketData:
        """Get current stock price"""
        try:
            if provider == MarketDataProvider.ALPHA_VANTAGE:
                return await self._get_alpha_vantage_quote(symbol)
            elif provider == MarketDataProvider.YAHOO_FINANCE:
                return await self._get_yahoo_finance_quote(symbol)
            else:
                raise ValueError(f"Unsupported provider: {provider.value}")
                
        except Exception as e:
            self.logger.error(f"Stock price fetch failed: {str(e)}")
            raise

    async def _get_alpha_vantage_quote(self, symbol: str) -> MarketData:
        """Get quote from Alpha Vantage"""
        # Simplified implementation
        return MarketData(
            symbol=symbol,
            provider=MarketDataProvider.ALPHA_VANTAGE.value,
            price=Decimal("100.00"),
            currency="USD",
            timestamp=datetime.now()
        )

    async def _get_yahoo_finance_quote(self, symbol: str) -> MarketData:
        """Get quote from Yahoo Finance"""
        # Simplified implementation
        return MarketData(
            symbol=symbol,
            provider=MarketDataProvider.YAHOO_FINANCE.value,
            price=Decimal("100.00"),
            currency="USD",
            timestamp=datetime.now()
        )

    async def get_forex_rate(self, from_currency: str, to_currency: str) -> MarketData:
        """Get foreign exchange rate"""
        try:
            symbol = f"{from_currency}{to_currency}"
            
            # Use Alpha Vantage forex API
            async with aiohttp.ClientSession() as session:
                params = {
                    "function": "FX_INTRADAY",
                    "from_symbol": from_currency,
                    "to_symbol": to_currency,
                    "interval": "1min",
                    "apikey": "demo"  # Would use actual API key
                }
                
                async with session.get(
                    self.providers[MarketDataProvider.ALPHA_VANTAGE.value]["base_url"],
                    params=params
                ) as response:
                    if response.status == 200:
                        # Simplified parsing
                        return MarketData(
                            symbol=symbol,
                            provider=MarketDataProvider.ALPHA_VANTAGE.value,
                            price=Decimal("1.0"),
                            currency=to_currency,
                            timestamp=datetime.now()
                        )
                    else:
                        raise ValueError("Forex rate fetch failed")
                        
        except Exception as e:
            self.logger.error(f"Forex rate fetch failed: {str(e)}")
            raise

class AdvancedIntegrationsOrchestrator:
    """
    Main orchestrator for all financial integrations
    """
    
    def __init__(self):
        self.banking = BankingIntegration()
        self.accounting = AccountingIntegration()
        self.market_data = MarketDataIntegration()
        self.logger = logging.getLogger(__name__)

    async def setup_tenant_integrations(self, tenant_id: str, 
                                      config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup all integrations for a tenant"""
        try:
            results = {
                "banking": [],
                "accounting": [],
                "market_data": []
            }
            
            # Setup banking integrations
            if "banking" in config:
                for bank_config in config["banking"]:
                    provider = BankingProvider(bank_config["provider"])
                    result = await self.banking.connect_bank_account(
                        provider, bank_config["credentials"], tenant_id
                    )
                    results["banking"].append(result)
            
            # Setup accounting integrations
            if "accounting" in config:
                for acc_config in config["accounting"]:
                    provider = AccountingProvider(acc_config["provider"])
                    result = await self.accounting.connect_accounting_system(
                        provider, acc_config["credentials"], tenant_id
                    )
                    results["accounting"].append(result)
            
            # Market data doesn't require per-tenant setup
            results["market_data"] = {"status": "available"}
            
            return {
                "tenant_id": tenant_id,
                "integrations": results,
                "setup_completed": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Integration setup failed: {str(e)}")
            raise

    async def get_unified_financial_data(self, tenant_id: str) -> Dict[str, Any]:
        """Get unified view of all financial data"""
        try:
            # Aggregate data from all sources
            accounts = [
                {
                    "account_id": acc.account_id,
                    "provider": acc.provider,
                    "balance": float(acc.balance),
                    "currency": acc.currency,
                    "last_updated": acc.last_updated.isoformat()
                }
                for acc in self.banking.accounts.values()
            ]
            
            # Recent transactions
            recent_transactions = [
                {
                    "transaction_id": txn.transaction_id,
                    "account_id": txn.account_id,
                    "amount": float(txn.amount),
                    "currency": txn.currency,
                    "type": txn.transaction_type.value,
                    "description": txn.description,
                    "date": txn.date.isoformat()
                }
                for txn in self.banking.transactions[-50:]  # Last 50 transactions
            ]
            
            # Market data
            market_summary = [
                {
                    "symbol": data.symbol,
                    "price": float(data.price),
                    "currency": data.currency,
                    "timestamp": data.timestamp.isoformat()
                }
                for data in self.market_data.market_data[-10:]  # Last 10 quotes
            ]
            
            return {
                "tenant_id": tenant_id,
                "accounts": accounts,
                "recent_transactions": recent_transactions,
                "market_data": market_summary,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Unified data fetch failed: {str(e)}")
            raise

# Initialize the integrations orchestrator
integrations_orchestrator = AdvancedIntegrationsOrchestrator()