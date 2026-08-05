# ============================================================
# chat.py - مدل‌های چت‌بات و پردازش زبان طبیعی
# ============================================================
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Index, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, List, Dict, Any

Base = declarative_base()


# ============================================================
# مدل مکالمات
# ============================================================

class ChatConversation(Base):
    """
    جدول مکالمات چات
    """
    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True, nullable=True)  # می‌تواند مهمان باشد
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=True)

    # موقعیت مکانی
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    region = Column(String(100), nullable=True)

    # وضعیت
    is_active = Column(Boolean, default=True)
    message_count = Column(Integer, default=0)

    # زمان‌ها
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow)

    # روابط
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_conversation_user_created', 'user_id', 'created_at'),
        Index('idx_conversation_session', 'session_id'),
        Index('idx_conversation_active', 'is_active'),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "title": self.title,
            "message_count": self.message_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
        }


# ============================================================
# مدل پیام‌های چات
# ============================================================

class ChatMessage(Base):
    """
    جدول پیام‌های چات
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id"), index=True, nullable=False)

    # محتوای پیام
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=True)

    # اطلاعات پردازش
    intent = Column(String(50), index=True, nullable=True)
    confidence = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)  # زمان پردازش به میلی‌ثانیه

    # موجودیت‌ها و داده‌های جانبی
    entities = Column(JSON, nullable=True)  # [{name, type, value}]
    location = Column(JSON, nullable=True)  # {lat, lng, address}
    context_data = Column(JSON, nullable=True)  # داده‌های اضافی

    # سنجه‌ها
    is_helpful = Column(Integer, nullable=True)  # 1=مفید، -1=غیرمفید
    is_rated = Column(Boolean, default=False)

    # زمان
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # روابط
    conversation = relationship("ChatConversation", back_populates="messages")

    __table_args__ = (
        Index('idx_message_conversation_created', 'conversation_id', 'created_at'),
        Index('idx_message_intent', 'intent'),
        Index('idx_message_helpful', 'is_helpful'),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "user_message": self.user_message,
            "bot_response": self.bot_response,
            "intent": self.intent,
            "confidence": self.confidence,
            "processing_time": self.processing_time,
            "entities": self.entities,
            "location": self.location,
            "is_helpful": self.is_helpful,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================
# مدل نیت‌های چات‌بات (ChatIntent)
# ============================================================

class ChatIntent(Base):
    """
    جدول نیت‌های چات‌بات (طبقه‌بندی)
    """
    __tablename__ = "chat_intents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)  # hospital, restaurant, taxi
    display_name = Column(String(100), nullable=True)  # نام نمایشی فارسی

    # الگوها و کلمات کلیدی
    patterns = Column(JSON, nullable=True)  # ["بیمارستان", "بیمار", "درمان"]
    keywords = Column(JSON, nullable=True)  # ["بیمارستان", "درمانگاه"]

    # پاسخ‌های پیش‌فرض
    response_template = Column(Text, nullable=True)
    fallback_response = Column(Text, nullable=True)

    # نوع موجودیت مرتبط
    entity_type = Column(String(50), nullable=True)  # service, location, person
    service_type = Column(String(50), nullable=True)  # hospital, restaurant, taxi

    # تنظیمات
    weight = Column(Integer, default=1)  # وزن برای تشخیص
    is_active = Column(Boolean, default=True)
    requires_location = Column(Boolean, default=False)

    # زمان
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_intent_name', 'name'),
        Index('idx_intent_active', 'is_active'),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "patterns": self.patterns,
            "keywords": self.keywords,
            "response_template": self.response_template,
            "entity_type": self.entity_type,
            "service_type": self.service_type,
            "weight": self.weight,
            "is_active": self.is_active,
            "requires_location": self.requires_location,
        }


# ============================================================
# مدل موجودیت‌ها (ChatEntity)
# ============================================================

class ChatEntity(Base):
    """
    جدول موجودیت‌ها (نام‌ها، مکان‌ها، سرویس‌ها)
    """
    __tablename__ = "chat_entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    display_name = Column(String(255), nullable=True)
    entity_type = Column(String(50), index=True, nullable=False)  # service, location, person, amenity

    # مترادف‌ها
    synonyms = Column(JSON, nullable=True)  # ["بیمارستان", "درمانگاه"]

    # اطلاعات تکمیلی
    description = Column(Text, nullable=True)
    entity_metadata = Column("metadata", JSON, nullable=True)  # اطلاعات اضافی

    # ارجاع به سرویس‌ها
    service_id = Column(Integer, nullable=True)  # ارجاع به جدول services
    service_type = Column(String(50), nullable=True)

    # موقعیت مکانی
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(String(500), nullable=True)

    # تنظیمات
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)

    # زمان
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_entity_type', 'entity_type'),
        Index('idx_entity_name_type', 'name', 'entity_type'),
        Index('idx_entity_active', 'is_active'),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "entity_type": self.entity_type,
            "synonyms": self.synonyms,
            "description": self.description,
            "metadata": self.extra_metadata,
            "service_id": self.service_id,
            "service_type": self.service_type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "is_active": self.is_active,
            "priority": self.priority,
        }

    def get_all_synonyms(self) -> List[str]:
        """دریافت تمام مترادف‌ها شامل نام اصلی"""
        result = [self.name]
        if self.synonyms:
            result.extend(self.synonyms)
        return result

    def matches_text(self, text: str) -> bool:
        """بررسی تطابق متن با موجودیت"""
        text_lower = text.lower()
        for synonym in self.get_all_synonyms():
            if synonym.lower() in text_lower:
                return True
        return False


# ============================================================
# مدل کش چات‌بات (ChatCache)
# ============================================================

class ChatCache(Base):
    """
    جدول کش برای پاسخ‌های چات‌بات (سرعت بالا)
    """
    __tablename__ = "chat_cache"

    id = Column(Integer, primary_key=True, index=True)
    query_hash = Column(String(100), unique=True, index=True, nullable=False)
    query_text = Column(Text, nullable=True)

    # پاسخ ذخیره شده
    response = Column(JSON, nullable=False)

    # آمار
    hits = Column(Integer, default=0)
    last_used = Column(DateTime, default=datetime.utcnow)

    # زمان
    ttl = Column(Integer, default=3600)  # ۱ ساعت
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, index=True)

    def is_expired(self) -> bool:
        """بررسی منقضی شدن کش"""
        return datetime.utcnow() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "query_hash": self.query_hash,
            "query_text": self.query_text,
            "response": self.response,
            "hits": self.hits,
            "ttl": self.ttl,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


# ============================================================
# داده‌های اولیه (Seed Data)
# ============================================================

def get_default_intents() -> List[Dict[str, Any]]:
    """دریافت نیت‌های پیش‌فرض"""
    return [
        {
            "name": "greeting",
            "display_name": "احوالپرسی",
            "patterns": ["سلام", "درود", "هی", "خوبی", "چطوری", "سلام علیکم"],
            "keywords": ["سلام", "درود"],
            "response_template": "سلام! 🌊 من دستیار هوشمند هرمزگان هستم. چطور می‌تونم کمکتون کنم؟",
            "entity_type": None,
            "service_type": None,
            "weight": 2,
            "requires_location": False,
        },
        {
            "name": "hospital",
            "display_name": "بیمارستان",
            "patterns": ["بیمارستان", "بیمار", "درمان", "داکتر", "پزشک", "اورژانس", "کلینیک", "درمانگاه"],
            "keywords": ["بیمارستان", "درمانگاه", "کلینیک"],
            "response_template": "نزدیک‌ترین بیمارستان‌ها را برای شما پیدا می‌کنم...",
            "entity_type": "service",
            "service_type": "hospital",
            "weight": 3,
            "requires_location": True,
        },
        {
            "name": "restaurant",
            "display_name": "رستوران",
            "patterns": ["رستوران", "غذا", "کباب", "شام", "ناهار", "کافه", "فست فود", "پیتزا"],
            "keywords": ["رستوران", "کافه", "غذاخوری"],
            "response_template": "بهترین رستوران‌های نزدیک شما را پیدا می‌کنم...",
            "entity_type": "service",
            "service_type": "restaurant",
            "weight": 3,
            "requires_location": True,
        },
        {
            "name": "taxi",
            "display_name": "تاکسی",
            "patterns": ["تاکسی", "خودرو", "رفتن", "حمل", "مسافر", "درخواست تاکسی", "اسنپ", "تپسی"],
            "keywords": ["تاکسی", "اسنپ", "تپسی"],
            "response_template": "درخواست تاکسی برای شما ثبت شد...",
            "entity_type": "service",
            "service_type": "taxi",
            "weight": 3,
            "requires_location": True,
        },
        {
            "name": "pharmacy",
            "display_name": "داروخانه",
            "patterns": ["داروخانه", "دارو", "قرص", "شربت", "نسخه", "بیماری", "درمانی"],
            "keywords": ["داروخانه", "دارو"],
            "response_template": "نزدیک‌ترین داروخانه‌ها را پیدا می‌کنم...",
            "entity_type": "service",
            "service_type": "pharmacy",
            "weight": 3,
            "requires_location": True,
        },
        {
            "name": "school",
            "display_name": "مدرسه",
            "patterns": ["مدرسه", "دانشگاه", "آموزش", "دانش‌آموز", "دانشجو", "کلاس", "معلم"],
            "keywords": ["مدرسه", "دانشگاه", "آموزشگاه"],
            "response_template": "مدارس و مراکز آموزشی نزدیک شما...",
            "entity_type": "service",
            "service_type": "school",
            "weight": 2,
            "requires_location": True,
        },
        {
            "name": "location",
            "display_name": "موقعیت مکانی",
            "patterns": ["کجا", "نزدیک", "فاصله", "موقعیت", "مکان", "آدرس", "محله", "منطقه", "شهر"],
            "keywords": ["موقعیت", "مکان", "آدرس"],
            "response_template": "موقعیت شما را بررسی می‌کنم...",
            "entity_type": "location",
            "service_type": None,
            "weight": 2,
            "requires_location": False,
        },
        {
            "name": "route",
            "display_name": "مسیریابی",
            "patterns": ["مسیریابی", "مسیر", "راه", "چگونه بروم", "رسیدن", "رفتن به", "نقشه"],
            "keywords": ["مسیر", "راه", "رفتن"],
            "response_template": "مسیر مورد نظر را محاسبه می‌کنم...",
            "entity_type": "location",
            "service_type": None,
            "weight": 3,
            "requires_location": True,
        },
        {
            "name": "camera",
            "display_name": "دوربین نظارتی",
            "patterns": ["دوربین", "نظارتی", "سرعت", "تخلف", "جریمه", "چراغ قرمز", "پلاک‌خوان"],
            "keywords": ["دوربین", "نظارتی"],
            "response_template": "دوربین‌های نظارتی نزدیک شما...",
            "entity_type": "camera",
            "service_type": "camera",
            "weight": 2,
            "requires_location": True,
        },
        {
            "name": "hotspot",
            "display_name": "نقطه حادثه‌خیز",
            "patterns": ["حادثه", "تصادف", "ترافیک", "خطرناک", "ایمنی", "مسدود", "بسته", "راه بندان"],
            "keywords": ["تصادف", "ترافیک", "خطرناک"],
            "response_template": "نقاط حادثه‌خیز نزدیک شما...",
            "entity_type": "hotspot",
            "service_type": "hotspot",
            "weight": 2,
            "requires_location": True,
        },
        {
            "name": "general",
            "display_name": "عمومی",
            "patterns": ["کمک", "راهنما", "خدمات", "اطلاعات", "پرسش", "سوال", "مشکل"],
            "keywords": ["کمک", "راهنما", "خدمات"],
            "response_template": "چطور می‌تونم کمکتون کنم؟ می‌تونم اطلاعات خدمات، بیمارستان‌ها یا رستوران‌ها را برای شما جستجو کنم.",
            "entity_type": None,
            "service_type": None,
            "weight": 1,
            "requires_location": False,
        },
    ]


def get_default_entities() -> List[Dict[str, Any]]:
    """دریافت موجودیت‌های پیش‌فرض"""
    return [
        {
            "name": "بیمارستان",
            "display_name": "بیمارستان",
            "entity_type": "service",
            "synonyms": ["درمانگاه", "کلینیک", "مرکز درمانی", "اورژانس"],
            "service_type": "hospital",
            "is_active": True,
            "priority": 10,
        },
        {
            "name": "رستوران",
            "display_name": "رستوران",
            "entity_type": "service",
            "synonyms": ["کافه", "فست فود", "غذاخوری", "رستوران سنتی"],
            "service_type": "restaurant",
            "is_active": True,
            "priority": 10,
        },
        {
            "name": "تاکسی",
            "display_name": "تاکسی",
            "entity_type": "service",
            "synonyms": ["اسنپ", "تپسی", "خودرو", "مسافربر"],
            "service_type": "taxi",
            "is_active": True,
            "priority": 10,
        },
        {
            "name": "داروخانه",
            "display_name": "داروخانه",
            "entity_type": "service",
            "synonyms": ["دارو", "درمانی", "بیماری"],
            "service_type": "pharmacy",
            "is_active": True,
            "priority": 10,
        },
        {
            "name": "مدرسه",
            "display_name": "مدرسه",
            "entity_type": "service",
            "synonyms": ["دانشگاه", "آموزشگاه", "مهدکودک"],
            "service_type": "school",
            "is_active": True,
            "priority": 10,
        },
        {
            "name": "بندرعباس",
            "display_name": "بندرعباس",
            "entity_type": "location",
            "synonyms": ["مرکز استان", "هرمزگان"],
            "service_type": None,
            "is_active": True,
            "priority": 10,
        },
        {
            "name": "قشم",
            "display_name": "قشم",
            "entity_type": "location",
            "synonyms": ["جزیره قشم"],
            "service_type": None,
            "is_active": True,
            "priority": 10,
        },
        {
            "name": "کیش",
            "display_name": "کیش",
            "entity_type": "location",
            "synonyms": ["جزیره کیش"],
            "service_type": None,
            "is_active": True,
            "priority": 10,
        },
    ]


# ============================================================
# Export کردن کلاس‌ها
# ============================================================

__all__ = [
    'ChatConversation',
    'ChatMessage',
    'ChatIntent',
    'ChatEntity',
    'ChatCache',
    'get_default_intents',
    'get_default_entities',
]


# ============================================================
# تست سریع
# ============================================================
if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    print("=" * 60)
    print("💬 تست مدل‌های چات")
    print("=" * 60)

    # ایجاد دیتابیس تست
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # تست ایجاد نیت
    print("\n📝 ایجاد نیت‌های پیش‌فرض:")
    intents = get_default_intents()
    for intent_data in intents:
        intent = ChatIntent(**intent_data)
        db.add(intent)
    db.commit()

    intents_count = db.query(ChatIntent).count()
    print(f"  {intents_count} نیت ایجاد شد")

    # تست ایجاد موجودیت
    print("\n📝 ایجاد موجودیت‌های پیش‌فرض:")
    entities = get_default_entities()
    for entity_data in entities:
        entity = ChatEntity(**entity_data)
        db.add(entity)
    db.commit()

    entities_count = db.query(ChatEntity).count()
    print(f"  {entities_count} موجودیت ایجاد شد")

    # تست کوئری
    print("\n🔍 تست جستجو:")
    hospital_intent = db.query(ChatIntent).filter(ChatIntent.name == "hospital").first()
    if hospital_intent:
        print(f"  نیت: {hospital_intent.display_name}")
        print(f"  الگوها: {hospital_intent.patterns}")

    entity = db.query(ChatEntity).filter(ChatEntity.name == "بیمارستان").first()
    if entity:
        print(f"  موجودیت: {entity.display_name}")
        print(f"  مترادف‌ها: {entity.synonyms}")
        print(f"  همه مترادف‌ها: {entity.get_all_synonyms()}")

    # تست تطابق
    print("\n✅ تست تطابق:")
    test_text = "نزدیک‌ترین بیمارستان کجاست؟"
    for intent in db.query(ChatIntent).filter(ChatIntent.is_active == True).all():
        if intent.patterns:
            for pattern in intent.patterns:
                if pattern in test_text:
                    print(f"  ✓ تطابق با نیت '{intent.display_name}': '{pattern}'")
                    break

    print("\n✅ تست مدل‌های چات با موفقیت انجام شد!")
    print("\n📋 کلاس‌های موجود:")
    print("  - ChatConversation")
    print("  - ChatMessage")
    print("  - ChatIntent")
    print("  - ChatEntity")
    print("  - ChatCache")
