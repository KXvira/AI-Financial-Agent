"""
QR Code Generator for Receipts

Generates QR codes for receipt verification.
"""

import qrcode
import io
from typing import Optional
import base64


class QRCodeGenerator:
    """QR code generator for receipts"""
    
    def __init__(
        self,
        box_size: int = 10,
        border: int = 2,
        fill_color: str = "black",
        back_color: str = "white"
    ):
        """
        Initialize QR code generator
        
        Args:
            box_size: Size of each box in pixels
            border: Border size in boxes
            fill_color: QR code color
            back_color: Background color
        """
        self.box_size = box_size
        self.border = border
        self.fill_color = fill_color
        self.back_color = back_color
    
    def generate_receipt_qr_data(
        self,
        receipt_number: str,
        amount: float,
        customer_name: str,
        payment_date: str,
        verification_url: Optional[str] = None
    ) -> str:
        """
        Generate QR code data string for receipt
        
        Args:
            receipt_number: Receipt number
            amount: Transaction amount
            customer_name: Customer name
            payment_date: Payment date
            verification_url: Optional verification URL
            
        Returns:
            QR code data string
        """
        if verification_url:
            # If verification URL provided, use it
            qr_data = f"{verification_url}?receipt={receipt_number}"
        else:
            # Otherwise, create structured data
            qr_data = (
                f"RECEIPT:{receipt_number}\n"
                f"AMOUNT:{amount}\n"
                f"CUSTOMER:{customer_name}\n"
                f"DATE:{payment_date}"
            )
        
        return qr_data
    
    def generate_qr_code(
        self,
        data: str,
        output_format: str = "PNG"
    ) -> bytes:
        """
        Generate QR code image
        
        Args:
            data: Data to encode in QR code
            output_format: Image format (PNG, JPEG, etc.)
            
        Returns:
            QR code image as bytes
        """
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,  # Auto-size
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=self.box_size,
            border=self.border,
        )
        
        # Add data
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(
            fill_color=self.fill_color,
            back_color=self.back_color
        )
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=output_format)
        img_bytes.seek(0)
        
        return img_bytes.read()
    
    def generate_qr_code_base64(
        self,
        data: str,
        output_format: str = "PNG"
    ) -> str:
        """
        Generate QR code image as base64 string
        
        Args:
            data: Data to encode in QR code
            output_format: Image format (PNG, JPEG, etc.)
            
        Returns:
            Base64 encoded QR code image
        """
        qr_bytes = self.generate_qr_code(data, output_format)
        return base64.b64encode(qr_bytes).decode('utf-8')
    
    def save_qr_code(
        self,
        data: str,
        file_path: str,
        output_format: str = "PNG"
    ) -> None:
        """
        Generate and save QR code to file
        
        Args:
            data: Data to encode in QR code
            file_path: Output file path
            output_format: Image format (PNG, JPEG, etc.)
        """
        qr_bytes = self.generate_qr_code(data, output_format)
        
        with open(file_path, 'wb') as f:
            f.write(qr_bytes)


# Example usage
if __name__ == "__main__":
    generator = QRCodeGenerator()
    
    # Generate QR data
    qr_data = generator.generate_receipt_qr_data(
        receipt_number="RCP-2025-0001",
        amount=11600.00,
        customer_name="John Doe",
        payment_date="2025-01-12"
    )
    
    print(f"QR Data: {qr_data}")
    
    # Generate QR code and save
    generator.save_qr_code(qr_data, "test_receipt_qr.png")
    print("QR code saved to test_receipt_qr.png")
    
    # Generate base64 encoded QR code
    qr_base64 = generator.generate_qr_code_base64(qr_data)
    print(f"Base64 length: {len(qr_base64)}")
