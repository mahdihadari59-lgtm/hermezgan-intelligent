from typing import TypeVar, Generic, Type, Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from sqlalchemy.sql import text
from datetime import datetime

from app.models.base import BaseModel

ModelType = TypeVar('ModelType', bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    کلاس پایه Repository با عملیات CRUD
    """

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    # ============================================================
    # CREATE
    # ============================================================

    def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def create_bulk(self, items: List[Dict]) -> List[ModelType]:
        instances = [self.model(**item) for item in items]
        self.db.add_all(instances)
        self.db.commit()
        for instance in instances:
            self.db.refresh(instance)
        return instances

    def create_or_update(self, filters: Dict, values: Dict) -> ModelType:
        instance = self.db.query(self.model).filter_by(**filters).first()

        if instance:
            for key, value in values.items():
                setattr(instance, key, value)
            self.db.commit()
            self.db.refresh(instance)
            return instance

        return self.create(**{**filters, **values})

    # ============================================================
    # READ
    # ============================================================

    def get_by_id(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_by_ids(self, ids: List[int]) -> List[ModelType]:
        return self.db.query(self.model).filter(self.model.id.in_(ids)).all()

    def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        return self.db.query(self.model).filter(getattr(self.model, field) == value).first()

    def get_all_by_field(self, field: str, value: Any) -> List[ModelType]:
        return self.db.query(self.model).filter(getattr(self.model, field) == value).all()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = True
    ) -> List[ModelType]:
        query = self.db.query(self.model)

        if order_by and hasattr(self.model, order_by):
            order = desc(getattr(self.model, order_by)) if order_desc else asc(getattr(self.model, order_by))
            query = query.order_by(order)

        return query.offset(skip).limit(limit).all()

    def count(self, filters: Optional[Dict] = None) -> int:
        query = self.db.query(self.model)
        if filters:
            for key, value in filters.items():
                query = query.filter(getattr(self.model, key) == value)
        return query.count()

    def exists(self, **filters) -> bool:
        query = self.db.query(self.model)
        for key, value in filters.items():
            query = query.filter(getattr(self.model, key) == value)
        return query.first() is not None

    def filter(
        self,
        filters: Optional[Dict] = None,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = True
    ) -> List[ModelType]:
        query = self.db.query(self.model)

        if filters:
            for key, value in filters.items():
                if isinstance(value, dict):
                    if "like" in value:
                        query = query.filter(getattr(self.model, key).like(f"%{value['like']}%"))
                    elif "in" in value:
                        query = query.filter(getattr(self.model, key).in_(value["in"]))
                    elif "between" in value:
                        query = query.filter(getattr(self.model, key).between(value["between"][0], value["between"][1]))
                    elif "gt" in value:
                        query = query.filter(getattr(self.model, key) > value["gt"])
                    elif "gte" in value:
                        query = query.filter(getattr(self.model, key) >= value["gte"])
                    elif "lt" in value:
                        query = query.filter(getattr(self.model, key) < value["lt"])
                    elif "lte" in value:
                        query = query.filter(getattr(self.model, key) <= value["lte"])
                else:
                    query = query.filter(getattr(self.model, key) == value)

        if order_by and hasattr(self.model, order_by):
            order = desc(getattr(self.model, order_by)) if order_desc else asc(getattr(self.model, order_by))
            query = query.order_by(order)

        return query.offset(skip).limit(limit).all()

    def search(self, query: str, fields: List[str], limit: int = 20) -> List[ModelType]:
        search_query = self.db.query(self.model)
        conditions = []

        for field in fields:
            if hasattr(self.model, field):
                conditions.append(getattr(self.model, field).like(f"%{query}%"))

        if conditions:
            search_query = search_query.filter(or_(*conditions))

        return search_query.limit(limit).all()

    # ============================================================
    # UPDATE
    # ============================================================

    def update(self, id: int, **kwargs) -> Optional[ModelType]:
        instance = self.get_by_id(id)
        if not instance:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        self.db.commit()
        self.db.refresh(instance)
        return instance

    def update_bulk(self, ids: List[int], **kwargs) -> int:
        updated = self.db.query(self.model).filter(self.model.id.in_(ids)).update(kwargs, synchronize_session=False)
        self.db.commit()
        return updated

    def increment(self, id: int, field: str, amount: int = 1) -> Optional[ModelType]:
        instance = self.get_by_id(id)
        if not instance:
            return None

        if hasattr(instance, field):
            current = getattr(instance, field) or 0
            setattr(instance, field, current + amount)

        self.db.commit()
        self.db.refresh(instance)
        return instance

    def decrement(self, id: int, field: str, amount: int = 1) -> Optional[ModelType]:
        return self.increment(id, field, -amount)

    # ============================================================
    # DELETE
    # ============================================================

    def delete(self, id: int) -> bool:
        instance = self.get_by_id(id)
        if not instance:
            return False

        self.db.delete(instance)
        self.db.commit()
        return True

    def delete_bulk(self, ids: List[int]) -> int:
        deleted = self.db.query(self.model).filter(self.model.id.in_(ids)).delete(synchronize_session=False)
        self.db.commit()
        return deleted

    def delete_all(self) -> int:
        deleted = self.db.query(self.model).delete(synchronize_session=False)
        self.db.commit()
        return deleted

    def soft_delete(self, id: int) -> Optional[ModelType]:
        instance = self.get_by_id(id)
        if not instance:
            return None

        if hasattr(instance, 'is_deleted') and hasattr(instance, 'deleted_at'):
            instance.is_deleted = True
            instance.deleted_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(instance)
            return instance

        return None

    def restore(self, id: int) -> Optional[ModelType]:
        instance = self.get_by_id(id)
        if not instance:
            return None

        if hasattr(instance, 'is_deleted') and hasattr(instance, 'deleted_at'):
            instance.is_deleted = False
            instance.deleted_at = None
            self.db.commit()
            self.db.refresh(instance)
            return instance

        return None

    # ============================================================
    # AGGREGATE
    # ============================================================

    def aggregate_sum(self, field: str, filters: Optional[Dict] = None) -> float:
        query = self.db.query(func.sum(getattr(self.model, field)))
        if filters:
            for key, value in filters.items():
                query = query.filter(getattr(self.model, key) == value)
        return query.scalar() or 0

    def aggregate_avg(self, field: str, filters: Optional[Dict] = None) -> float:
        query = self.db.query(func.avg(getattr(self.model, field)))
        if filters:
            for key, value in filters.items():
                query = query.filter(getattr(self.model, key) == value)
        return query.scalar() or 0

    def aggregate_max(self, field: str, filters: Optional[Dict] = None) -> Any:
        query = self.db.query(func.max(getattr(self.model, field)))
        if filters:
            for key, value in filters.items():
                query = query.filter(getattr(self.model, key) == value)
        return query.scalar()

    def aggregate_min(self, field: str, filters: Optional[Dict] = None) -> Any:
        query = self.db.query(func.min(getattr(self.model, field)))
        if filters:
            for key, value in filters.items():
                query = query.filter(getattr(self.model, key) == value)
        return query.scalar()

    def aggregate_group_by(
        self,
        group_field: str,
        agg_field: str,
        agg_func: str = "count"
    ) -> List[Tuple]:
        agg_functions = {
            "count": func.count,
            "sum": func.sum,
            "avg": func.avg,
            "max": func.max,
            "min": func.min
        }

        func_agg = agg_functions.get(agg_func, func.count)
        query = self.db.query(
            getattr(self.model, group_field),
            func_agg(getattr(self.model, agg_field)).label("value")
        ).group_by(getattr(self.model, group_field))

        return query.all()
