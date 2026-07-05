"""Unit Tests for NLP Engine"""

import pytest
from app.core.nlp_engine import FarsiNLPEngine, get_nlp_engine

class TestFarsiNLPEngine:
    """Tests for Farsi NLP Engine"""
    
    @pytest.fixture
    def nlp_engine(self):
        """Initialize NLP engine for tests"""
        return FarsiNLPEngine()
    
    def test_normalize(self, nlp_engine):
        """Test text normalization"""
        text = "سلام     به     شما"  # Extra spaces
        normalized = nlp_engine.normalize(text)
        assert "سلام به شما" == normalized
    
    def test_tokenize(self, nlp_engine):
        """Test tokenization"""
        text = "سلام به شما"
        tokens = nlp_engine.tokenize(text)
        assert len(tokens) > 0
        assert "سلام" in tokens
    
    def test_lemmatize(self, nlp_engine):
        """Test lemmatization"""
        tokens = ["سلام", "به", "شما"]
        lemmas = nlp_engine.lemmatize(tokens)
        assert len(lemmas) == len(tokens)
        assert all(isinstance(l, str) for l in lemmas)
    
    def test_classify_intent_greeting(self, nlp_engine):
        """Test intent classification for greeting"""
        text = "سلام! خوبی؟"
        intent, confidence = nlp_engine.classify_intent(text)
        assert intent == "greeting"
        assert 0 <= confidence <= 1
    
    def test_classify_intent_location_query(self, nlp_engine):
        """Test intent classification for location query"""
        text = "نزدیک‌ترین بیمارستان کجاست؟"
        intent, confidence = nlp_engine.classify_intent(text)
        assert intent == "location_query"
        assert confidence > 0.8
    
    def test_classify_intent_direction(self, nlp_engine):
        """Test intent classification for direction"""
        text = "راه رفتن تا دانشگاه کجاست؟"
        intent, confidence = nlp_engine.classify_intent(text)
        assert intent == "direction"
        assert confidence > 0.7
    
    def test_get_embeddings(self, nlp_engine):
        """Test embedding generation"""
        text = "سلام به شما"
        embeddings = nlp_engine.get_embeddings(text)
        assert len(embeddings) > 0
        assert isinstance(embeddings, (list, type(None)))
    
    def test_process_full_pipeline(self, nlp_engine):
        """Test full NLP processing pipeline"""
        text = "نزدیک‌ترین بیمارستان کجاست؟"
        result = nlp_engine.process(text)
        
        assert result["original_text"] == text
        assert "normalized_text" in result
        assert "tokens" in result
        assert "lemmas" in result
        assert "intent" in result
        assert 0 <= result["intent_confidence"] <= 1
    
    def test_get_nlp_engine_singleton(self):
        """Test NLP engine singleton pattern"""
        engine1 = get_nlp_engine()
        engine2 = get_nlp_engine()
        assert engine1 is engine2


class TestNLPEdgeCases:
    """Edge case tests for NLP"""
    
    @pytest.fixture
    def nlp_engine(self):
        return FarsiNLPEngine()
    
    def test_empty_text(self, nlp_engine):
        """Test processing empty text"""
        text = ""
        result = nlp_engine.process(text)
        assert result["original_text"] == text
    
    def test_text_with_numbers(self, nlp_engine):
        """Test text with numbers"""
        text = "تلفن: ۰۷۶۳۳۳۳۱۰۰۰"
        result = nlp_engine.process(text)
        assert "تلفن" in result["tokens"]
    
    def test_text_with_english(self, nlp_engine):
        """Test mixed Farsi and English text"""
        text = "Hermezgan درهرمزگان"
        result = nlp_engine.process(text)
        assert len(result["tokens"]) > 0
    
    def test_very_long_text(self, nlp_engine):
        """Test processing very long text"""
        text = "سلام " * 100
        result = nlp_engine.process(text)
        assert len(result["tokens"]) > 0
    
    def test_special_characters(self, nlp_engine):
        """Test text with special characters"""
        text = "سلام!!! آپ کیسے ہو؟؟؟"
        result = nlp_engine.process(text)
        assert len(result["tokens"]) > 0
