"""
models.py

SQLAlchemy models for Hormozgan GeoData + Bandari Knowledge.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class BandariWord(Base):
    """Bandari dictionary words with dialect support."""
    __tablename__ = "bandari_words"

    id = Column(Integer, primary_key=True, index=True)
    word_standard = Column(String(200), nullable=False, index=True)
    word_bandari = Column(String(200), nullable=True, index=True)
    dialect_code = Column(String(10), nullable=False, default="ban")  # ban, min, qes, jas, lan, bas, kha, rud, sir
    category = Column(String(50), nullable=True)
    subcategory = Column(String(50), nullable=True)
    definition = Column(Text, nullable=True)
    example = Column(Text, nullable=True)
    ipa = Column(String(200), nullable=True)
    confidence_score = Column(Float, default=0.7)
    data_quality = Column(String(20), default="sourced")  # verified | sourced
    region_usage = Column(String(100), nullable=True)
    etymology = Column(String(100), nullable=True)
    cultural_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    translations = relationship("BandariTranslation", back_populates="word", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<BandariWord(id={self.id}, word={self.word_standard}, dialect={self.dialect_code})>"


class BandariTranslation(Base):
    """Cross-dialect translations."""
    __tablename__ = "bandari_translations"

    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("bandari_words.id"), nullable=False)
    target_dialect = Column(String(10), nullable=False)
    translation = Column(String(200), nullable=False)
    confidence = Column(Float, default=0.7)
    created_at = Column(DateTime, default=datetime.utcnow)

    word = relationship("BandariWord", back_populates="translations")


class LocalKnowledge(Base):
    """Local knowledge entries (cities, culture, food, etc.)."""
    __tablename__ = "local_knowledge"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)  # cities, culture, food, handicraft
    subcategory = Column(String(50), nullable=True)
    example = Column(Text, nullable=True)
    region = Column(String(100), nullable=True)
    source = Column(String(100), default="user-provided")
    confidence_score = Column(Float, default=85.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<LocalKnowledge(id={self.id}, title={self.title}, category={self.category})>"


class GrammarRule(Base):
    """Bandari grammar rules."""
    __tablename__ = "grammar_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    pattern = Column(String(500), nullable=False)
    replacement = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Idiom(Base):
    """Bandari idioms and proverbs."""
    __tablename__ = "idioms"

    id = Column(Integer, primary_key=True, index=True)
    term = Column(String(200), nullable=False, index=True)
    meaning = Column(Text, nullable=False)
    category = Column(String(50), nullable=True)
    example = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Dialogue(Base):
    """Bandari dialogues."""
    __tablename__ = "dialogues"

    id = Column(Integer, primary_key=True, index=True)
    scenario = Column(String(100), nullable=False)
    speaker = Column(String(50), nullable=False)
    text = Column(Text, nullable=False)
    translation = Column(Text, nullable=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
