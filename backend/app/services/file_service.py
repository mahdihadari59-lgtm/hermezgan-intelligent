import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
import logging

from app.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class FileService:
    """سرویس مدیریت فایل‌ها"""

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        # پوشه‌های فرعی
        self.subdirs = ["images", "documents", "audio", "video", "temp"]
        for subdir in self.subdirs:
            (self.upload_dir / subdir).mkdir(exist_ok=True)

    def save_file(
        self,
        file_content: bytes,
        filename: str,
        category: str = "documents",
        subfolder: Optional[str] = None
    ) -> Dict:
        """
        ذخیره فایل

        Args:
            file_content: محتوای فایل
            filename: نام فایل
            category: دسته (images, documents, audio, video)
            subfolder: زیرپوشه (اختیاری)

        Returns:
            Dict: اطلاعات فایل ذخیره شده

        Raises:
            ValidationError: اگر پسوند مجاز نباشد
        """
        # بررسی پسوند
        extension = Path(filename).suffix.lower()
        allowed_extensions = self._get_allowed_extensions(category)

        if extension not in allowed_extensions:
            raise ValidationError(f"پسوند {extension} برای دسته {category} مجاز نیست")

        # تولید نام یکتا
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        file_path = self.upload_dir / category

        if subfolder:
            file_path = file_path / subfolder
            file_path.mkdir(parents=True, exist_ok=True)

        file_path = file_path / unique_name

        # ذخیره فایل
        with open(file_path, "wb") as f:
            f.write(file_content)

        file_size = len(file_content)

        logger.info(f"📁 فایل ذخیره شد: {file_path} ({file_size} bytes)")

        return {
            "filename": unique_name,
            "original_name": filename,
            "path": str(file_path),
            "url": f"/uploads/{category}/{subfolder + '/' if subfolder else ''}{unique_name}",
            "size": file_size,
            "extension": extension,
            "category": category,
            "uploaded_at": datetime.utcnow().isoformat()
        }

    def delete_file(self, file_path: str) -> bool:
        """
        حذف فایل

        Args:
            file_path: مسیر فایل

        Returns:
            bool: موفقیت حذف
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"🗑️ فایل حذف شد: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ خطا در حذف فایل: {e}")
            return False

    def get_file_url(self, file_path: str) -> str:
        """دریافت URL فایل"""
        return f"/uploads/{file_path}"

    def _get_allowed_extensions(self, category: str) -> List[str]:
        """دریافت پسوندهای مجاز برای هر دسته"""
        extensions = {
            "images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
            "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"],
            "audio": [".mp3", ".wav", ".ogg", ".m4a"],
            "video": [".mp4", ".webm", ".avi", ".mov", ".mkv"],
            "temp": [".*"]  # همه پسوندها برای موقت
        }

        return extensions.get(category, [".*"])

    def get_file_size(self, file_path: str) -> Optional[int]:
        """دریافت حجم فایل"""
        try:
            return os.path.getsize(file_path)
        except Exception:
            return None
