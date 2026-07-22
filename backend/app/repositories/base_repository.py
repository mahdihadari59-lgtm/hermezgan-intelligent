from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models import Base

ModelType = TypeVar('ModelType', bound=Base)


class BaseRepository(Generic[ModelType]):
    """کلاس پایه برای تمام Repository‌ها"""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """دریافت رکورد بر اساس ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """دریافت تمام رکوردها با صفحه‌بندی"""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """دریافت رکورد بر اساس فیلد مشخص"""
        return self.db.query(self.model).filter(getattr(self.model, field) == value).first()

    def get_all_by_field(self, field: str, value: Any) -> List[ModelType]:
        """دریافت تمام رکوردها بر اساس فیلد مشخص"""
        return self.db.query(self.model).filter(getattr(self.model, field) == value).all()

    def count(self, filters: Optional[Dict] = None) -> int:
        """تعداد کل رکوردها"""
        query = self.db.query(self.model)
        if filters:
            for key, value in filters.items():
                query = query.filter(getattr(self.model, key) == value)
        return query.count()

    def create(self, **kwargs) -> ModelType:
        """ایجاد رکورد جدید"""
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def create_bulk(self, items: List[Dict]) -> List[ModelType]:
        """ایجاد چندین رکورد به صورت گروهی"""
        instances = [self.model(**item) for item in items]
        self.db.add_all(instances)
        self.db.commit()
        for instance in instances:
            self.db.refresh(instance)
        return instances

    def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """به‌روزرسانی رکورد"""
        instance = self.get_by_id(id)
        if not instance:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, id: int) -> bool:
        """حذف رکورد"""
        instance = self.get_by_id(id)
        if not instance:
            return False

        self.db.delete(instance)
        self.db.commit()
        return True

    def delete_bulk(self, ids: List[int]) -> int:
        """حذف چندین رکورد"""
        deleted = self.db.query(self.model).filter(self.model.id.in_(ids)).delete(synchronize_session=False)
        self.db.commit()
        return deleted

    def exists(self, **filters) -> bool:
        """بررسی وجود رکورد با فیلترهای مشخص"""
        query = self.db.query(self.model)
        for key, value in filters.items():
            query = query.filter(getattr(self.model, key) == value)
        return query.first() is not None
