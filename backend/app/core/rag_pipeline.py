"""RAG (Retrieval-Augmented Generation) Pipeline"""

import json
from typing import List, Dict, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger
from app.core.nlp_engine import get_nlp_engine

class RAGPipeline:
    """Retrieval-Augmented Generation Pipeline"""
    
    def __init__(self, db_connection=None):
        """Initialize RAG Pipeline"""
        logger.info("🚀 Initializing RAG Pipeline...")
        self.nlp_engine = get_nlp_engine()
        self.db_connection = db_connection
        self.knowledge_base = []  # Will be populated from DB
        self.embedding_cache = {}  # Cache for embeddings
        logger.info("✅ RAG Pipeline initialized")
    
    def load_knowledge_base(self, entities: List[Dict]) -> None:
        """Load knowledge base from entities"""
        logger.info(f"📚 Loading {len(entities)} entities into knowledge base...")
        
        self.knowledge_base = []
        for entity in entities:
            # Create document for each entity
            doc = {
                "entity_id": entity.get("entity_id"),
                "name": entity.get("name"),
                "type": entity.get("type"),
                "description": entity.get("description", ""),
                "content": self._create_entity_content(entity),
            }
            
            # Pre-compute embeddings
            embedding = self.nlp_engine.get_embeddings(doc["content"])
            doc["embedding"] = embedding.tolist() if len(embedding) > 0 else []
            
            self.knowledge_base.append(doc)
        
        logger.info(f"✅ Knowledge base loaded with {len(self.knowledge_base)} documents")
    
    def _create_entity_content(self, entity: Dict) -> str:
        """Create searchable content from entity"""
        parts = [
            entity.get("name", ""),
            entity.get("description", ""),
            entity.get("type", ""),
            entity.get("address", ""),
        ]
        return " ".join([str(p) for p in parts if p])
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve relevant documents for a query"""
        logger.info(f"🔍 Retrieving top {top_k} documents for query: {query}")
        
        if not self.knowledge_base:
            logger.warning("Knowledge base is empty")
            return []
        
        # Get query embedding
        query_embedding = self.nlp_engine.get_embeddings(query)
        
        if len(query_embedding) == 0:
            logger.warning("Could not generate query embedding")
            return []
        
        # Compute similarities
        similarities = []
        for doc in self.knowledge_base:
            if not doc["embedding"]:
                similarities.append(0.0)
                continue
            
            similarity = cosine_similarity(
                [query_embedding],
                [np.array(doc["embedding"])]
            )[0][0]
            similarities.append(similarity)
        
        # Get top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]
        retrieved_docs = [
            {
                **self.knowledge_base[i],
                "similarity_score": float(similarities[i])
            }
            for i in top_indices
            if similarities[i] > 0.3  # Minimum similarity threshold
        ]
        
        logger.info(f"✅ Retrieved {len(retrieved_docs)} relevant documents")
        return retrieved_docs
    
    def generate_context(self, retrieved_docs: List[Dict]) -> str:
        """Generate context from retrieved documents"""
        if not retrieved_docs:
            return "بدون اطلاعات مرتبط"
        
        context_parts = []
        for doc in retrieved_docs:
            part = f"\n{doc['name']} ({doc['type']}):\n{doc['content']}"
            context_parts.append(part)
        
        return "\n".join(context_parts)
    
    def generate_response(self, query: str, context: str, intent: str) -> str:
        """Generate response based on context (simplified version)"""
        logger.info(f"📝 Generating response for intent: {intent}")
        
        # Simple template-based response generation
        response_templates = {
            "location_query": "اطلاعات درخواستی: {context}",
            "direction": "مسیریابی: {context}",
            "service_inquiry": "خدمات مورد نیاز: {context}",
            "greeting": "سلام! چطور می‌توانم کمکتون کنم؟",
        }
        
        template = response_templates.get(intent, "پاسخ: {context}")
        response = template.format(context=context)
        
        return response
    
    def process(self, query: str) -> Dict:
        """Full RAG processing pipeline"""
        logger.info(f"🔄 RAG Processing: {query}")
        
        # Step 1: NLP Processing
        nlp_result = self.nlp_engine.process(query)
        
        # Step 2: Retrieve relevant documents
        retrieved_docs = self.retrieve(query, top_k=5)
        
        # Step 3: Generate context
        context = self.generate_context(retrieved_docs)
        
        # Step 4: Generate response
        response = self.generate_response(
            query,
            context,
            nlp_result["intent"]
        )
        
        result = {
            "query": query,
            "nlp_result": nlp_result,
            "retrieved_documents": retrieved_docs,
            "context": context,
            "response": response,
            "intent": nlp_result["intent"],
        }
        
        logger.info(f"✅ RAG processing complete")
        return result


# Global RAG Pipeline Instance
rag_pipeline = None

def get_rag_pipeline(db_connection=None) -> RAGPipeline:
    """Get or initialize RAG pipeline"""
    global rag_pipeline
    if rag_pipeline is None:
        rag_pipeline = RAGPipeline(db_connection)
    return rag_pipeline
