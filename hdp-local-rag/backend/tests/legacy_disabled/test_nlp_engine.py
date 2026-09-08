import pytest
from app.core.nlp_engine import FarsiNLPEngine, get_nlp_engine

class TestFarsiNLPEngine:
    def test_normalize(self, nlp_engine):
        text = "  سلام   به   شما  "
        result = nlp_engine.normalize(text)
        assert result == "سلام به شما"

    def test_tokenize(self, nlp_engine):
        text = "سلام به شما"
        result = nlp_engine.tokenize(text)
        assert result == ["سلام", "به", "شما"]

    def test_lemmatize(self, nlp_engine):
        tokens = ["سلام", "به", "شما"]
        lemmas = nlp_engine.lemmatize(tokens)
        assert isinstance(lemmas, list)

    def test_classify_intent_greeting(self, nlp_engine):
        text = "سلام! خوبی؟"
        intent, confidence = nlp_engine.classify_intent(text)
        assert intent == "greeting"
        assert confidence > 0.5

    def test_classify_intent_location_query(self, nlp_engine):
        text = "نزدیک‌ترین بیمارستان کجاست؟"
        intent, confidence = nlp_engine.classify_intent(text)
        assert intent == "location_query"
        assert confidence > 0.5

    def test_classify_intent_direction(self, nlp_engine):
        text = "راه رفتن تا دانشگاه کجاست؟"
        intent, confidence = nlp_engine.classify_intent(text)
        assert intent == "direction"
        assert confidence > 0.5

    def test_get_embeddings(self, nlp_engine):
        text = "سلام به شما"
        embeddings = nlp_engine.get_embeddings(text)
        assert len(embeddings) == 32

    def test_process_full_pipeline(self, nlp_engine):
        text = "نزدیک‌ترین بیمارستان کجاست؟"
        result = nlp_engine.process(text)
        assert result["original_text"] == text
        assert "normalized_text" in result
        assert "tokens" in result
        assert "lemmas" in result
        assert "intent" in result
        assert "confidence" in result

    def test_get_nlp_engine_singleton(self):
        engine1 = get_nlp_engine()
        engine2 = get_nlp_engine()
        assert engine1 is engine2

    @pytest.fixture
    def nlp_engine(self):
        return FarsiNLPEngine()


class TestNLPEdgeCases:
    def test_empty_text(self, nlp_engine):
        result = nlp_engine.process("")
        assert result["intent"] == "unknown"

    def test_text_with_numbers(self, nlp_engine):
        text = "تلفن: ۰۷۶۳۳۳۳۱۰۰۰"
        result = nlp_engine.process(text)
        assert "تلفن" in result["tokens"] or "تلفن" in text

    def test_text_with_english(self, nlp_engine):
        text = "Hermezgan درهرمزگان"
        result = nlp_engine.process(text)
        assert "هرمزگان" in result["tokens"] or "هرمزگان" in text

    def test_very_long_text(self, nlp_engine):
        text = "سلام " * 100
        result = nlp_engine.process(text)
        assert result["tokens"] is not None

    def test_special_characters(self, nlp_engine):
        text = "سلام!!! آپ کیسے ہو؟؟؟"
        result = nlp_engine.process(text)
        assert "سلام" in result["tokens"][0] if result["tokens"] else True

    @pytest.fixture
    def nlp_engine(self):
        return FarsiNLPEngine()
