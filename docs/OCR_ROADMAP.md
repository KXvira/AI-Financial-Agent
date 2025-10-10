# Real OCR Implementation Roadmap

## Phase 1: Foundation & Infrastructure (Week 1-2)

### 1.1 Dependencies & Environment Setup
```bash
# Enhanced OCR dependencies
pip install easyocr>=1.7.0          # Alternative to Tesseract
pip install pdf2image>=1.16.3       # PDF processing  
pip install paddleocr>=2.7.0        # Chinese/Multi-language OCR
pip install redis>=4.5.0            # Task queue
pip install celery>=5.3.4           # Background processing
pip install supervision>=0.16.0     # Computer vision utilities
```

### 1.2 Enhanced File Upload System
**Current Status**: Basic uploader exists
**Improvements Needed**:
- Multi-file drag & drop support
- Real-time upload progress
- File compression and optimization
- PDF to image conversion
- Mobile camera integration

### 1.3 Background Processing Setup
**Celery Configuration**:
```python
# backend/celery_app.py
from celery import Celery

celery_app = Celery(
    "financial_agent",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["backend.ocr.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Nairobi",
    enable_utc=True,
)
```

## Phase 2: Core OCR Engine (Week 3-4)

### 2.1 Multi-Engine OCR Processing
**Implementation Priority**:
1. **Tesseract OCR** (Primary) - Good for English text
2. **EasyOCR** (Secondary) - Better for handwritten text
3. **PaddleOCR** (Fallback) - Multi-language support

**Processing Pipeline**:
```python
class AdvancedOCRProcessor:
    def __init__(self):
        self.tesseract = TesseractProcessor()
        self.easyocr = EasyOCRProcessor()
        self.paddle = PaddleOCRProcessor()
    
    async def process_receipt(self, image_path: str) -> OCRResult:
        # Try multiple OCR engines and combine results
        results = []
        
        # Primary: Tesseract
        tesseract_result = await self.tesseract.extract_text(image_path)
        results.append(tesseract_result)
        
        # Secondary: EasyOCR (if Tesseract confidence is low)
        if tesseract_result.confidence < 0.7:
            easyocr_result = await self.easyocr.extract_text(image_path)
            results.append(easyocr_result)
        
        # Combine and validate results
        return self.combine_results(results)
```

### 2.2 Image Preprocessing Pipeline
**Enhancements**:
- Auto-rotation detection
- Perspective correction
- Noise reduction
- Contrast enhancement
- Shadow removal

**Implementation**:
```python
def preprocess_image(self, image_path: str) -> str:
    # Load image
    image = cv2.imread(image_path)
    
    # Auto-rotate
    image = self.auto_rotate(image)
    
    # Perspective correction
    image = self.correct_perspective(image)
    
    # Enhance contrast
    image = self.enhance_contrast(image)
    
    # Denoise
    image = self.denoise(image)
    
    # Save processed image
    processed_path = self.save_processed_image(image)
    return processed_path
```

### 2.3 Kenyan Business Receipt Patterns
**Local Business Optimization**:
```python
KENYAN_BUSINESS_PATTERNS = {
    'currency': [
        r'ksh[:\s]*(\d+[\.,]\d{2})',
        r'kes[:\s]*(\d+[\.,]\d{2})',
        r'(\d+[\.,]\d{2})\s*kes',
        r'total[:\s]*(\d+[\.,]\d{2})'
    ],
    'tax_numbers': [
        r'pin[:\s]*([a-z]\d{9}[a-z])',
        r'vat[:\s]*(\d{10})',
        r'kra[:\s]*([a-z]\d{9}[a-z])'
    ],
    'mpesa': [
        r'mpesa[:\s]*([a-z0-9]{10})',
        r'transaction[:\s]*([a-z0-9]+)',
        r'reference[:\s]*([a-z0-9]+)'
    ],
    'common_vendors': [
        'nakumatt', 'tuskys', 'naivas', 'carrefour',
        'java house', 'artcaffe', 'dormans',
        'shell', 'total', 'kenol', 'ola'
    ]
}
```

## Phase 3: AI-Powered Expense Extraction (Week 5-6)

### 3.1 Gemini AI Integration Enhancement
**Current**: Basic AI service exists
**Enhancements Needed**:
- Receipt-specific prompts
- Structured data extraction
- Confidence scoring
- Error correction

**Enhanced Gemini Service**:
```python
class EnhancedGeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
    async def extract_receipt_data(self, ocr_text: str, image_path: str) -> ReceiptData:
        prompt = self.build_receipt_extraction_prompt(ocr_text)
        
        # Include image for better context
        image = Image.open(image_path)
        
        response = await self.model.generate_content([prompt, image])
        
        return self.parse_structured_response(response.text)
    
    def build_receipt_extraction_prompt(self, ocr_text: str) -> str:
        return f"""
        Analyze this Kenyan business receipt and extract the following information:
        
        OCR Text: {ocr_text}
        
        Extract and format as JSON:
        {{
            "vendor": {{
                "name": "vendor name",
                "address": "vendor address",
                "phone": "phone number",
                "pin_number": "KRA PIN if available"
            }},
            "transaction": {{
                "date": "YYYY-MM-DD",
                "time": "HH:MM",
                "reference": "transaction reference",
                "receipt_number": "receipt number"
            }},
            "items": [
                {{
                    "description": "item description",
                    "quantity": 1,
                    "unit_price": 0.00,
                    "total": 0.00
                }}
            ],
            "totals": {{
                "subtotal": 0.00,
                "tax": 0.00,
                "total": 0.00,
                "currency": "KES"
            }},
            "payment": {{
                "method": "cash|mpesa|card",
                "reference": "payment reference if available"
            }},
            "category": "office_supplies|transport|meals|utilities|other",
            "confidence": 0.95
        }}
        
        Focus on Kenyan business formats and KES currency.
        If information is unclear, set confidence lower and mark fields as null.
        """
```

### 3.2 Smart Categorization System
**ML-based Category Prediction**:
```python
class ExpenseCategorizer:
    def __init__(self):
        self.categories = ExpenseCategory
        self.vendor_categories = self.load_vendor_mappings()
        
    def categorize_expense(self, receipt_data: ReceiptData) -> ExpenseCategory:
        # Vendor-based categorization
        if receipt_data.vendor.name:
            category = self.categorize_by_vendor(receipt_data.vendor.name)
            if category:
                return category
        
        # Description-based categorization
        category = self.categorize_by_items(receipt_data.items)
        if category:
            return category
            
        # Amount-based heuristics
        return self.categorize_by_amount(receipt_data.totals.total)
    
    def load_vendor_mappings(self) -> Dict[str, ExpenseCategory]:
        return {
            'nakumatt': ExpenseCategory.OFFICE_SUPPLIES,
            'shell': ExpenseCategory.FUEL,
            'java house': ExpenseCategory.MEALS,
            'uber': ExpenseCategory.TRANSPORT,
            'bolt': ExpenseCategory.TRANSPORT,
            'safaricom': ExpenseCategory.TELECOMMUNICATIONS,
            # ... more mappings
        }
```

## Phase 4: Real-time Processing & UI (Week 7-8)

### 4.1 WebSocket Integration for Real-time Updates
**Backend WebSocket**:
```python
from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_processing_update(self, receipt_id: str, status: str, data: dict):
        message = {
            "receipt_id": receipt_id,
            "status": status,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### 4.2 Enhanced Frontend Components
**Real-time Receipt Processing UI**:
```tsx
// components/ReceiptProcessor.tsx
import { useWebSocket } from '@/hooks/useWebSocket';

export default function ReceiptProcessor() {
    const { socket, messages } = useWebSocket('/ws/user123');
    const [processingReceipts, setProcessingReceipts] = useState<ProcessingReceipt[]>([]);
    
    useEffect(() => {
        socket?.on('processing_update', (data) => {
            setProcessingReceipts(prev => 
                prev.map(receipt => 
                    receipt.id === data.receipt_id 
                        ? { ...receipt, ...data }
                        : receipt
                )
            );
        });
    }, [socket]);
    
    return (
        <div className="space-y-4">
            {processingReceipts.map(receipt => (
                <ReceiptProcessingCard 
                    key={receipt.id}
                    receipt={receipt}
                />
            ))}
        </div>
    );
}
```

### 4.3 Mobile Camera Integration
**Camera Capture Component**:
```tsx
// components/CameraCapture.tsx
import { useRef, useState } from 'react';

export default function CameraCapture({ onCapture }: { onCapture: (file: File) => void }) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [stream, setStream] = useState<MediaStream | null>(null);
    
    const startCamera = async () => {
        try {
            const mediaStream = await navigator.mediaDevices.getUserMedia({
                video: { 
                    facingMode: 'environment',  // Use back camera
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            });
            setStream(mediaStream);
            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
            }
        } catch (error) {
            console.error('Error accessing camera:', error);
        }
    };
    
    const capturePhoto = () => {
        if (videoRef.current && canvasRef.current) {
            const video = videoRef.current;
            const canvas = canvasRef.current;
            const context = canvas.getContext('2d');
            
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            context?.drawImage(video, 0, 0);
            
            canvas.toBlob((blob) => {
                if (blob) {
                    const file = new File([blob], 'receipt.jpg', { type: 'image/jpeg' });
                    onCapture(file);
                }
            }, 'image/jpeg', 0.9);
        }
    };
    
    return (
        <div className="camera-container">
            <video ref={videoRef} autoPlay muted />
            <canvas ref={canvasRef} style={{ display: 'none' }} />
            <div className="camera-controls">
                <button onClick={startCamera}>Start Camera</button>
                <button onClick={capturePhoto}>Capture</button>
            </div>
        </div>
    );
}
```

## Phase 5: Advanced Features & Optimization (Week 9-10)

### 5.1 Batch Processing
**Bulk Upload Handler**:
```python
@router.post("/upload/batch")
async def upload_batch_receipts(
    files: List[UploadFile],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Upload multiple receipts for batch processing"""
    receipt_ids = []
    
    for file in files:
        # Upload each file
        upload_response = await upload_receipt(file, current_user)
        receipt_ids.append(upload_response.receipt_id)
    
    # Process all receipts in background
    background_tasks.add_task(
        process_batch_receipts,
        receipt_ids,
        current_user.id
    )
    
    return {
        "message": f"Batch upload successful. Processing {len(files)} receipts.",
        "receipt_ids": receipt_ids
    }
```

### 5.2 Data Validation & Correction
**User Correction Interface**:
```tsx
// components/ReceiptCorrection.tsx
export default function ReceiptCorrection({ receipt }: { receipt: Receipt }) {
    const [corrections, setCorrections] = useState<Partial<Receipt>>(receipt);
    const [isEditing, setIsEditing] = useState(false);
    
    const saveCorrections = async () => {
        try {
            await fetch(`/api/receipts/${receipt.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(corrections)
            });
            setIsEditing(false);
        } catch (error) {
            console.error('Failed to save corrections:', error);
        }
    };
    
    return (
        <div className="receipt-correction">
            {isEditing ? (
                <div className="edit-form">
                    <input 
                        value={corrections.vendor?.name || ''} 
                        onChange={(e) => setCorrections(prev => ({
                            ...prev,
                            vendor: { ...prev.vendor, name: e.target.value }
                        }))}
                    />
                    <input 
                        type="number"
                        value={corrections.total_amount || 0} 
                        onChange={(e) => setCorrections(prev => ({
                            ...prev,
                            total_amount: parseFloat(e.target.value)
                        }))}
                    />
                    <button onClick={saveCorrections}>Save</button>
                    <button onClick={() => setIsEditing(false)}>Cancel</button>
                </div>
            ) : (
                <div className="view-mode">
                    <button onClick={() => setIsEditing(true)}>Edit</button>
                </div>
            )}
        </div>
    );
}
```

### 5.3 Advanced Analytics
**Receipt Analytics Dashboard**:
```python
class ReceiptAnalytics:
    def __init__(self, db: Database):
        self.db = db
    
    async def generate_insights(self, user_id: str) -> ReceiptInsights:
        receipts = await self.get_user_receipts(user_id, limit=1000)
        
        return ReceiptInsights(
            spending_trends=self.analyze_spending_trends(receipts),
            top_categories=self.get_top_categories(receipts),
            vendor_analysis=self.analyze_vendors(receipts),
            cost_optimization=self.suggest_optimizations(receipts),
            tax_deductions=self.identify_tax_deductions(receipts)
        )
    
    def analyze_spending_trends(self, receipts: List[Receipt]) -> Dict[str, Any]:
        # Monthly spending analysis
        monthly_data = defaultdict(float)
        
        for receipt in receipts:
            month_key = receipt.date.strftime('%Y-%m')
            monthly_data[month_key] += receipt.total_amount
        
        return {
            'monthly_totals': dict(monthly_data),
            'trend': self.calculate_trend(monthly_data),
            'seasonal_patterns': self.identify_patterns(monthly_data)
        }
```

## Phase 6: Production Deployment & Monitoring (Week 11-12)

### 6.1 Performance Optimization
**Caching Strategy**:
```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=1)

def cache_result(expiry_seconds: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Check cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(
                cache_key, 
                expiry_seconds, 
                json.dumps(result, default=str)
            )
            
            return result
        return wrapper
    return decorator

@cache_result(expiry_seconds=1800)  # 30 minutes
async def get_expense_summary(user_id: str) -> ExpenseSummary:
    # ... implementation
```

### 6.2 Monitoring & Logging
**OCR Processing Metrics**:
```python
import time
from prometheus_client import Counter, Histogram

# Metrics
ocr_requests_total = Counter('ocr_requests_total', 'Total OCR requests', ['status'])
ocr_processing_time = Histogram('ocr_processing_seconds', 'OCR processing time')
ocr_accuracy_score = Histogram('ocr_accuracy_score', 'OCR accuracy scores')

class OCRMetrics:
    @staticmethod
    def track_processing_time(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                ocr_requests_total.labels(status='success').inc()
                return result
            except Exception as e:
                ocr_requests_total.labels(status='error').inc()
                raise
            finally:
                processing_time = time.time() - start_time
                ocr_processing_time.observe(processing_time)
        return wrapper
```

## Implementation Priority Matrix

| Phase | Feature | Priority | Effort | Impact |
|-------|---------|----------|--------|--------|
| 1 | File Upload Enhancement | High | Medium | High |
| 1 | Background Processing | High | Medium | High |
| 2 | Multi-Engine OCR | High | High | High |
| 2 | Image Preprocessing | Medium | Medium | Medium |
| 3 | AI Data Extraction | High | High | High |
| 3 | Smart Categorization | Medium | Medium | High |
| 4 | Real-time Updates | Medium | Medium | High |
| 4 | Mobile Camera | Low | Medium | Medium |
| 5 | Batch Processing | Low | Low | Medium |
| 5 | User Corrections | Medium | Medium | High |
| 6 | Performance Optimization | High | Medium | High |
| 6 | Monitoring | Medium | Low | Medium |

## Success Metrics

### Technical Metrics
- **OCR Accuracy**: >95% for printed receipts, >85% for handwritten
- **Processing Time**: <30 seconds per receipt
- **Success Rate**: >98% successful processing
- **Uptime**: 99.9% availability

### Business Metrics
- **User Adoption**: Track upload frequency and user engagement
- **Data Quality**: Measure correction rates and confidence scores
- **Cost Efficiency**: Monitor processing costs vs. business value
- **User Satisfaction**: Collect feedback on accuracy and usability

## Resource Requirements

### Infrastructure
- **CPU**: Multi-core processors for image processing
- **RAM**: 8GB+ for large image processing
- **Storage**: 500GB+ for receipt images and processed data
- **Redis**: For task queue and caching
- **GPU**: Optional, for advanced ML models

### External Services
- **Google Cloud Vision API**: Backup OCR service
- **AWS Textract**: Alternative OCR service
- **Tesseract**: Primary OCR engine
- **EasyOCR**: Secondary OCR engine

### Team Requirements
- **Backend Developer**: FastAPI, OCR integration
- **Frontend Developer**: React, real-time UI
- **ML Engineer**: OCR optimization, AI integration
- **DevOps Engineer**: Deployment, monitoring

---

This roadmap provides a comprehensive path from the current demo system to a production-ready OCR solution. Each phase builds upon the previous one, ensuring steady progress while maintaining system stability.