from sqlalchemy import Column, Integer, DateTime, Boolean, func
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime
from app.database.session import Base


class BaseModel(Base):
    """کلاس پایه برای تمام مدل‌ها"""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def to_dict(self) -> dict:
        """تبدیل مدل به دیکشنری"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def to_json(self) -> dict:
        """تبدیل مدل به JSON با فرمت مناسب"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result


class TimestampMixin:
    """میکسین زمان‌ها"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SoftDeleteMixin:
    """میکسین حذف نرم"""
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    def soft_delete(self):
        """حذف نرم"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self):
        """بازیابی"""
        self.is_deleted = False
        self.deleted_at = None
