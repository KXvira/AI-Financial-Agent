"""
File Upload Handler for Receipt Processing
"""
import os
import uuid
import shutil
from typing import Optional, List, Tuple
from fastapi import UploadFile, HTTPException, status
from pathlib import Path
import magic
from PIL import Image, ImageOps
import logging

from .models import ProcessingStatus, FileUploadResponse

logger = logging.getLogger("financial-agent.ocr.uploader")

class FileUploader:
    """Handle file uploads for receipt processing"""
    
    def __init__(self, upload_dir: str = "uploads/receipts"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_mime_types = {
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif',
            'application/pdf'
        }
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf'}
        
    def validate_file(self, file: UploadFile) -> Tuple[bool, str]:
        """Validate uploaded file"""
        try:
            # Check file size
            if hasattr(file, 'size') and file.size > self.max_file_size:
                return False, f"File too large. Maximum size is {self.max_file_size / 1024 / 1024:.1f}MB"
            
            # Check file extension
            if file.filename:
                file_ext = Path(file.filename).suffix.lower()
                if file_ext not in self.allowed_extensions:
                    return False, f"File type not supported. Allowed types: {', '.join(self.allowed_extensions)}"
            
            # Read a small portion to check MIME type
            file_content = file.file.read(2048)
            file.file.seek(0)  # Reset file pointer
            
            # Use python-magic to detect MIME type
            try:
                mime_type = magic.from_buffer(file_content, mime=True)
                if mime_type not in self.allowed_mime_types:
                    return False, f"Invalid file type detected: {mime_type}"
            except Exception:
                # Fallback to extension-based validation if magic fails
                logger.warning("MIME type detection failed, using extension validation")
            
            return True, "File validation passed"
            
        except Exception as e:
            logger.error(f"File validation error: {str(e)}")
            return False, f"File validation failed: {str(e)}"
    
    async def upload_file(self, file: UploadFile, user_id: str) -> FileUploadResponse:
        """Upload and save receipt file"""
        try:
            # Validate file
            is_valid, message = self.validate_file(file)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=message
                )
            
            # Generate unique receipt ID and filename
            receipt_id = str(uuid.uuid4())
            file_extension = Path(file.filename).suffix.lower() if file.filename else '.jpg'
            safe_filename = f"{receipt_id}{file_extension}"
            
            # Create user directory
            user_dir = self.upload_dir / user_id
            user_dir.mkdir(exist_ok=True)
            
            # Save file
            file_path = user_dir / safe_filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Get file size
            file_size = file_path.stat().st_size
            
            # Optimize image if it's an image file
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
                await self._optimize_image(file_path)
            
            logger.info(f"File uploaded successfully: {file_path}")
            
            return FileUploadResponse(
                receipt_id=receipt_id,
                filename=safe_filename,
                file_size=file_size,
                upload_status="success",
                message="File uploaded successfully",
                processing_status=ProcessingStatus.PENDING
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"File upload error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File upload failed: {str(e)}"
            )
    
    async def _optimize_image(self, file_path: Path) -> None:
        """Optimize uploaded image for better OCR processing"""
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Auto-orient image based on EXIF data
                img = ImageOps.exif_transpose(img)
                
                # Resize if too large (max 2048px on longer side)
                max_dimension = 2048
                if max(img.size) > max_dimension:
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                
                # Save optimized image
                img.save(file_path, optimize=True, quality=85)
                
            logger.info(f"Image optimized: {file_path}")
            
        except Exception as e:
            logger.warning(f"Image optimization failed: {str(e)}")
            # Continue without optimization if it fails
    
    def get_file_path(self, user_id: str, filename: str) -> Path:
        """Get full file path for a user's receipt"""
        return self.upload_dir / user_id / filename
    
    def delete_file(self, user_id: str, filename: str) -> bool:
        """Delete a receipt file"""
        try:
            file_path = self.get_file_path(user_id, filename)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
        except Exception as e:
            logger.error(f"File deletion error: {str(e)}")
            return False
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """Clean up temporary files older than specified age"""
        import time
        
        cleaned_count = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        try:
            for file_path in self.upload_dir.rglob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        cleaned_count += 1
                        logger.info(f"Cleaned up old file: {file_path}")
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
        
        return cleaned_count
    
    def get_storage_stats(self) -> dict:
        """Get storage statistics"""
        try:
            total_files = 0
            total_size = 0
            
            for file_path in self.upload_dir.rglob("*"):
                if file_path.is_file():
                    total_files += 1
                    total_size += file_path.stat().st_size
            
            return {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "upload_directory": str(self.upload_dir)
            }
        except Exception as e:
            logger.error(f"Storage stats error: {str(e)}")
            return {
                "error": str(e),
                "total_files": 0,
                "total_size_bytes": 0
            }