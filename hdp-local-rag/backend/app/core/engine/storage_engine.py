import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any, BinaryIO
from datetime import datetime
import hashlib
import uuid
import logging
from urllib.parse import urlparse

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageEngine:
    """
    موتور ذخیره‌سازی فایل‌ها
    پشتیبانی از Local, S3, FTP
    """

    def __init__(self):
        self.base_dir = Path(settings.UPLOAD_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.subdirs = {
            "images": self.base_dir / "images",
            "documents": self.base_dir / "documents",
            "audio": self.base_dir / "audio",
            "video": self.base_dir / "video",
            "temp": self.base_dir / "temp"
        }

        for subdir in self.subdirs.values():
            subdir.mkdir(exist_ok=True)

        self.s3_enabled = bool(os.getenv("AWS_ACCESS_KEY_ID"))
        self.s3_bucket = os.getenv("AWS_S3_BUCKET", "hermezgan-uploads")

        if self.s3_enabled:
            try:
                import boto3
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    region_name=os.getenv("AWS_REGION", "us-east-1")
                )
                logger.info("✅ S3 storage enabled")
            except Exception as e:
                logger.warning(f"⚠️ S3 initialization failed: {e}")
                self.s3_enabled = False

    def save(
        self,
        file_content: bytes,
        filename: str,
        category: str = "documents",
        subfolder: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        file_hash = hashlib.md5(file_content).hexdigest()[:8]
        unique_name = f"{file_hash}_{uuid.uuid4().hex[:8]}_{filename}"
        file_path = self.subdirs.get(category, self.base_dir / category)

        if subfolder:
            file_path = file_path / subfolder
            file_path.mkdir(parents=True, exist_ok=True)

        full_path = file_path / unique_name

        if self.s3_enabled:
            url = self._save_to_s3(file_content, unique_name, category, subfolder)
        else:
            url = self._save_to_local(file_content, full_path)

        file_size = len(file_content)

        result = {
            "filename": unique_name,
            "original_name": filename,
            "path": str(full_path) if not self.s3_enabled else unique_name,
            "url": url,
            "size": file_size,
            "hash": file_hash,
            "category": category,
            "subfolder": subfolder,
            "uploaded_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }

        logger.info(f"📁 File saved: {filename} ({file_size} bytes)")
        return result

    def _save_to_local(self, file_content: bytes, path: Path) -> str:
        with open(path, "wb") as f:
            f.write(file_content)
        return f"/uploads/{path.relative_to(self.base_dir)}"

    def _save_to_s3(self, file_content: bytes, filename: str, category: str, subfolder: Optional[str] = None) -> str:
        key = f"{category}"
        if subfolder:
            key = f"{key}/{subfolder}"
        key = f"{key}/{filename}"

        self.s3_client.put_object(
            Bucket=self.s3_bucket,
            Key=key,
            Body=file_content,
            ContentType=self._get_content_type(filename)
        )

        return f"https://{self.s3_bucket}.s3.amazonaws.com/{key}"

    def delete(self, file_path: str) -> bool:
        try:
            if file_path.startswith("https://") and "s3" in file_path:
                return self._delete_from_s3(file_path)

            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"🗑️ File deleted: {file_path}")
                return True

            return False

        except Exception as e:
            logger.error(f"❌ Error deleting file: {e}")
            return False

    def _delete_from_s3(self, url: str) -> bool:
        parsed = urlparse(url)
        key = parsed.path.lstrip('/')
        self.s3_client.delete_object(Bucket=self.s3_bucket, Key=key)
        logger.info(f"🗑️ S3 file deleted: {key}")
        return True

    def get_url(self, file_path: str) -> str:
        if file_path.startswith("http"):
            return file_path
        return f"/uploads/{file_path}"

    def get_file_info(self, file_path: str) -> Optional[Dict]:
        path = Path(file_path)
        if not path.exists():
            return None

        stat = path.stat()
        return {
            "name": path.name,
            "size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "is_file": path.is_file(),
            "extension": path.suffix
        }

    def _get_content_type(self, filename: str) -> str:
        extensions = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".mp4": "video/mp4",
            ".webm": "video/webm",
            ".txt": "text/plain"
        }

        ext = Path(filename).suffix.lower()
        return extensions.get(ext, "application/octet-stream")


_storage_engine = None


def get_storage_engine() -> StorageEngine:
    global _storage_engine
    if _storage_engine is None:
        _storage_engine = StorageEngine()
    return _storage_engine


def get_storage() -> StorageEngine:
    return get_storage_engine()
