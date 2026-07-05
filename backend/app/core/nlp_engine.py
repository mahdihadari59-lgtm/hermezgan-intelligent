"""NLP Engine for Farsi Text Processing"""

import re
from typing import List, Tuple, Dict
from hazm import Normalizer, Tokenizer, POSTagger, Lemmatizer
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import numpy as np
from loguru import logger

class FarsiNLPEngine:
    """Farsi Natural Language Processing Engine"""
    
    def __init__(self):
        """Initialize Farsi NLP components"""
        logger.info("🚀 Initializing Farsi NLP Engine...")
        
        # Hazm components for Farsi
        self.normalizer = Normalizer()
        self.tokenizer = Tokenizer()
        self.lemmatizer = Lemmatizer()
        
        # Intent detection with zero-shot classification
        try:
            self.intent_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
        except Exception as e:
            logger.warning(f"⚠️ Intent classifier not loaded: {e}")
            self.intent_classifier = None
        
        # NER model
        try:
            self.ner_pipeline = pipeline(
                "token-classification",
                model="HooshvareLab/persian-ner-bert"
            )
        except Exception as e:
            logger.warning(f"⚠️ NER model not loaded: {e}")
            self.ner_pipeline = None
        
        # Embedding model
        try:
            self.embedding_model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            self.embedding_tokenizer = AutoTokenizer.from_pretrained(self.embedding_model_name)
            self.embedding_model = AutoModel.from_pretrained(self.embedding_model_name)
        except Exception as e:
            logger.warning(f"⚠️ Embedding model not loaded: {e}")
            self.embedding_model = None
        
        # Intent patterns for Farsi
        self.intent_patterns = {
            "location_query": [
                r"(نزدیک|قریب|کجا|کدام|چه|کدوم)",
                r"(بیمارستان|مدرسه|دانشگاه|دفتر|اداره|بانک)",
                r"(بیمارستان|داروخانه|دکتر)",
            ],
            "direction": [
                r"(راه|مسیر|جاده|خیابان|راستا)",
                r"(برو|رفتن|حرکت)",
            ],
            "service_inquiry": [
                r"(تلفن|ساعت|وقت|شماره|آدرس)",
                r"(خدمات|سرویس)",
            ],
            "greeting": [
                r"(سلام|خوبی|چطوری|حالت|حالا)",
                r"(صبح بخیر|شب بخیر|درود)",
            ],
        }
        
        logger.info("✅ Farsi NLP Engine initialized successfully")
    
    def normalize(self, text: str) -> str:
        """Normalize Farsi text"""
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        # Hazm normalization
        text = self.normalizer.normalize(text)
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize Farsi text"""
        normalized = self.normalize(text)
        tokens = self.tokenizer.tokenize(normalized)
        return tokens
    
    def lemmatize(self, tokens: List[str]) -> List[str]:
        """Lemmatize tokens"""
        lemmas = [self.lemmatizer.lemmatize(token) for token in tokens]
        return lemmas
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract Named Entities from text"""
        if self.ner_pipeline is None:
            logger.warning("NER pipeline not available")
            return []
        
        try:
            entities = self.ner_pipeline(text)
            return entities
        except Exception as e:
            logger.error(f"Entity extraction error: {e}")
            return []
    
    def classify_intent(self, text: str, candidate_labels: List[str] = None) -> Tuple[str, float]:
        """Classify user intent"""
        if candidate_labels is None:
            candidate_labels = [
                "location_query",
                "direction",
                "service_inquiry",
                "greeting",
                "other"
            ]
        
        # Pattern-based classification first (faster)
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return intent, 0.95
        
        # Transformer-based classification
        if self.intent_classifier:
            try:
                result = self.intent_classifier(text, candidate_labels)
                return result['labels'][0], result['scores'][0]
            except Exception as e:
                logger.error(f"Intent classification error: {e}")
                return "other", 0.5
        
        return "other", 0.5
    
    def get_embeddings(self, text: str) -> np.ndarray:
        """Get sentence embeddings"""
        if self.embedding_model is None:
            logger.warning("Embedding model not available")
            return np.array([])
        
        try:
            inputs = self.embedding_tokenizer(
                text,
                padding=True,
                truncation=True,
                return_tensors="pt"
            )
            
            with torch.no_grad():
                outputs = self.embedding_model(**inputs)
            
            # Mean pooling
            embeddings = outputs.last_hidden_state.mean(dim=1)
            return embeddings.cpu().numpy()[0]
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return np.array([])
    
    def process(self, text: str) -> Dict:
        """Full NLP processing pipeline"""
        logger.info(f"Processing text: {text[:50]}...")
        
        # Step 1: Normalize
        normalized_text = self.normalize(text)
        
        # Step 2: Tokenize
        tokens = self.tokenize(normalized_text)
        
        # Step 3: Lemmatize
        lemmas = self.lemmatize(tokens)
        
        # Step 4: Extract entities
        entities = self.extract_entities(normalized_text)
        
        # Step 5: Classify intent
        intent, intent_confidence = self.classify_intent(normalized_text)
        
        # Step 6: Get embeddings
        embeddings = self.get_embeddings(normalized_text)
        
        result = {
            "original_text": text,
            "normalized_text": normalized_text,
            "tokens": tokens,
            "lemmas": lemmas,
            "entities": entities,
            "intent": intent,
            "intent_confidence": float(intent_confidence),
            "embeddings": embeddings.tolist() if len(embeddings) > 0 else [],
        }
        
        logger.info(f"✅ Processing complete. Intent: {intent}")
        return result


# Global NLP Engine Instance
nlp_engine = None

def get_nlp_engine() -> FarsiNLPEngine:
    """Get or initialize NLP engine"""
    global nlp_engine
    if nlp_engine is None:
        nlp_engine = FarsiNLPEngine()
    return nlp_engine
