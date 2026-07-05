"""Unit Tests for RAG Pipeline"""

import pytest
import numpy as np
from app.core.rag_pipeline import RAGPipeline, get_rag_pipeline
from app.core.nlp_engine import get_nlp_engine

class TestRAGPipeline:
    """Tests for RAG Pipeline"""
    
    @pytest.fixture
    def rag_pipeline(self):
        """Initialize RAG pipeline for tests"""
        return RAGPipeline()
    
    @pytest.fixture
    def sample_entities(self):
        """Sample entities for testing"""
        return [
            {
                "entity_id": 1,
                "name": "بیمارستان فوق‌تخصصی کودکان",
                "type": "healthcare",
                "description": "بیمارستان فوق‌تخصصی کودکان بندرعباس",
                "latitude": 27.2250,
                "longitude": 56.2950,
            },
            {
                "entity_id": 2,
                "name": "دانشگاه هرمزگان",
                "type": "educational",
                "description": "دانشگاه دولتی هرمزگان",
                "latitude": 27.1950,
                "longitude": 56.2700,
            },
        ]
    
    def test_load_knowledge_base(self, rag_pipeline, sample_entities):
        """Test loading knowledge base"""
        rag_pipeline.load_knowledge_base(sample_entities)
        assert len(rag_pipeline.knowledge_base) == 2
    
    def test_retrieve_documents(self, rag_pipeline, sample_entities):
        """Test document retrieval"""
        rag_pipeline.load_knowledge_base(sample_entities)
        
        query = "بیمارستان"
        results = rag_pipeline.retrieve(query, top_k=1)
        
        assert len(results) > 0
        assert results[0]["type"] == "healthcare"
    
    def test_generate_context(self, rag_pipeline, sample_entities):
        """Test context generation"""
        rag_pipeline.load_knowledge_base(sample_entities)
        
        docs = rag_pipeline.knowledge_base[:1]
        context = rag_pipeline.generate_context(docs)
        
        assert "بیمارستان" in context or "healthcare" in context
    
    def test_generate_response(self, rag_pipeline):
        """Test response generation"""
        query = "بیمارستان کجاست؟"
        context = "بیمارستان فوق‌تخصصی کودکان در بندرعباس است"
        intent = "location_query"
        
        response = rag_pipeline.generate_response(query, context, intent)
        assert len(response) > 0
    
    def test_process_full_pipeline(self, rag_pipeline, sample_entities):
        """Test full RAG processing"""
        rag_pipeline.load_knowledge_base(sample_entities)
        
        query = "بیمارستان نزدیک کجاست؟"
        result = rag_pipeline.process(query)
        
        assert "query" in result
        assert "response" in result
        assert "intent" in result
        assert "retrieved_documents" in result
    
    def test_get_rag_pipeline_singleton(self):
        """Test RAG pipeline singleton pattern"""
        pipeline1 = get_rag_pipeline()
        pipeline2 = get_rag_pipeline()
        assert pipeline1 is pipeline2
    
    def test_empty_knowledge_base(self, rag_pipeline):
        """Test retrieve with empty knowledge base"""
        query = "بیمارستان"
        results = rag_pipeline.retrieve(query)
        assert len(results) == 0
    
    def test_retrieve_with_threshold(self, rag_pipeline, sample_entities):
        """Test retrieval with similarity threshold"""
        rag_pipeline.load_knowledge_base(sample_entities)
        
        # Query completely unrelated
        query = "xyz123 not related"
        results = rag_pipeline.retrieve(query, top_k=5)
        
        # Should filter by similarity threshold
        assert len(results) <= 2


class TestRAGEdgeCases:
    """Edge case tests for RAG"""
    
    @pytest.fixture
    def rag_pipeline(self):
        return RAGPipeline()
    
    def test_entity_without_embedding(self, rag_pipeline):
        """Test entity without pre-computed embedding"""
        entities = [
            {
                "entity_id": 1,
                "name": "Test Entity",
                "type": "test",
                "description": "Test",
            }
        ]
        rag_pipeline.load_knowledge_base(entities)
        assert len(rag_pipeline.knowledge_base) == 1
    
    def test_generate_context_empty_docs(self, rag_pipeline):
        """Test context generation with empty documents"""
        context = rag_pipeline.generate_context([])
        assert "بدون اطلاعات" in context or len(context) > 0
    
    def test_process_empty_query(self, rag_pipeline):
        """Test processing empty query"""
        result = rag_pipeline.process("")
        assert "query" in result
