#!/usr/bin/env python3
"""
Simple HTTP server for OCR API testing using only Python standard library
"""

import json
import os
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import tempfile
import base64

class OCRTestHandler(BaseHTTPRequestHandler):
    # In-memory storage for testing
    receipts_store = {}
    
    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    def _send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def _mock_ocr_processing(self, filename):
        """Mock OCR processing for testing purposes"""
        if "receipt" in filename.lower():
            return {
                "vendor": "Sample Store Ltd",
                "total": 1250.50,
                "date": "2024-10-06",
                "category": "Office Supplies",
                "items": [
                    {"name": "Paper A4", "price": 500.00, "quantity": 2},
                    {"name": "Pens", "price": 250.50, "quantity": 1}
                ],
                "confidence": 0.85
            }
        elif "fuel" in filename.lower():
            return {
                "vendor": "Shell Station",
                "total": 3500.00,
                "date": "2024-10-06",
                "category": "Transport",
                "items": [
                    {"name": "Petrol", "price": 3500.00, "quantity": 25}
                ],
                "confidence": 0.92
            }
        else:
            return {
                "vendor": "Unknown Vendor",
                "total": 750.00,
                "date": "2024-10-06",
                "category": "Other",
                "items": [],
                "confidence": 0.65
            }
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == '/':
                self._send_json_response({
                    "message": "OCR Test Server is running",
                    "endpoints": [
                        "/api/ocr/upload-receipt",
                        "/api/ocr/receipts", 
                        "/api/ocr/expense-summary",
                        "/api/ocr/health"
                    ]
                })
            
            elif path == '/api/ocr/receipts':
                self._send_json_response({
                    "receipts": list(self.receipts_store.values()),
                    "total": len(self.receipts_store)
                })
            
            elif path.startswith('/api/ocr/receipts/'):
                receipt_id = path.split('/')[-1]
                if receipt_id in self.receipts_store:
                    self._send_json_response(self.receipts_store[receipt_id])
                else:
                    self._send_json_response({"error": "Receipt not found"}, 404)
            
            elif path == '/api/ocr/expense-summary':
                receipts = list(self.receipts_store.values())
                total_expenses = sum(r["parsed_data"]["total"] for r in receipts)
                
                # Category summary
                category_summary = {}
                for receipt in receipts:
                    category = receipt["parsed_data"]["category"]
                    amount = receipt["parsed_data"]["total"]
                    category_summary[category] = category_summary.get(category, 0) + amount
                
                # Recent expenses
                recent_expenses = [
                    {
                        "id": r["id"],
                        "date": r["parsed_data"]["date"],
                        "vendor": r["parsed_data"]["vendor"],
                        "amount": r["parsed_data"]["total"],
                        "category": r["parsed_data"]["category"],
                        "status": r["status"]
                    }
                    for r in receipts[-10:]
                ]
                
                self._send_json_response({
                    "totalExpenses": total_expenses,
                    "monthlyTotal": total_expenses,
                    "categorySummary": category_summary,
                    "recentExpenses": recent_expenses
                })
            
            elif path == '/api/ocr/health':
                self._send_json_response({
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "receipts_count": len(self.receipts_store),
                    "ocr_service": "mock_active"
                })
            
            else:
                self._send_json_response({"error": "Not found"}, 404)
                
        except Exception as e:
            self._send_json_response({"error": str(e)}, 500)
    
    def do_POST(self):
        if self.path == '/api/ocr/upload-receipt':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # Simple multipart parsing for demo (normally would use proper parser)
                # For this test, we'll just simulate successful upload
                filename = f"test_receipt_{datetime.now().strftime('%H%M%S')}.jpg"
                
                # Generate unique ID
                receipt_id = str(uuid.uuid4())
                
                # Mock OCR processing
                ocr_result = self._mock_ocr_processing(filename)
                
                # Store receipt data
                receipt_data = {
                    "id": receipt_id,
                    "filename": filename,
                    "status": "completed",
                    "uploaded_at": datetime.now().isoformat(),
                    "parsed_data": ocr_result,
                    "file_size": len(post_data)
                }
                
                self.receipts_store[receipt_id] = receipt_data
                
                self._send_json_response({
                    "success": True,
                    "receipt_id": receipt_id,
                    "parsed_data": ocr_result,
                    "status": "completed"
                })
                
            except Exception as e:
                self._send_json_response({"error": f"Upload failed: {str(e)}"}, 500)
        else:
            self._send_json_response({"error": "Not found"}, 404)
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def start_server(port=8000):
    """Start the OCR test server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, OCRTestHandler)
    
    print(f"🚀 OCR Test Server starting on http://localhost:{port}")
    print(f"📊 Dashboard: http://localhost:{port}")
    print(f"📁 Upload endpoint: http://localhost:{port}/api/ocr/upload-receipt")
    print(f"📈 Health check: http://localhost:{port}/api/ocr/health")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        httpd.server_close()

if __name__ == "__main__":
    start_server(8000)