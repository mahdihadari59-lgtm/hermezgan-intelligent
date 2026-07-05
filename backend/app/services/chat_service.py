"""Chat Service - Handle conversations and chat logic"""

from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger
from app.core.rag_pipeline import get_rag_pipeline
from app.core.nlp_engine import get_nlp_engine
from app.core.location_service import get_location_service

class ChatService:
    """Chat Service for handling conversations"""
    
    def __init__(self, db_connection=None):
        """Initialize Chat Service"""
        logger.info("🚀 Initializing Chat Service...")
        self.rag_pipeline = get_rag_pipeline(db_connection)
        self.nlp_engine = get_nlp_engine()
        self.location_service = get_location_service()
        self.db_connection = db_connection
        logger.info("✅ Chat Service initialized")
    
    def process_message(self, message: str, user_id: str, user_location: Optional[Dict] = None) -> Dict:
        """Process user message and generate response"""
        logger.info(f"💬 Processing message from {user_id}: {message[:50]}...")
        
        # Step 1: NLP Processing
        nlp_result = self.nlp_engine.process(message)
        intent = nlp_result["intent"]
        
        # Step 2: RAG Processing
        rag_result = self.rag_pipeline.process(message)
        
        # Step 3: Context-aware response generation
        response = self._generate_context_aware_response(
            message,
            intent,
            rag_result,
            user_location,
            nlp_result
        )
        
        # Step 4: Prepare chat result
        chat_result = {
            "user_id": user_id,
            "message": message,
            "response": response,
            "intent": intent,
            "confidence": nlp_result["intent_confidence"],
            "entities": nlp_result["entities"],
            "timestamp": datetime.now().isoformat(),
            "retrieved_documents": rag_result["retrieved_documents"],
        }
        
        # Step 5: Save to database (if available)
        if self.db_connection:
            self._save_chat_history(chat_result)
        
        logger.info(f"✅ Message processed. Intent: {intent}")
        return chat_result
    
    def _generate_context_aware_response(
        self,
        message: str,
        intent: str,
        rag_result: Dict,
        user_location: Optional[Dict],
        nlp_result: Dict
    ) -> str:
        """Generate context-aware response based on intent and location"""
        logger.info(f"📝 Generating context-aware response for intent: {intent}")
        
        response = ""
        
        if intent == "greeting":
            response = "سلام! خوش‌آمدید به سیستم هوشمند هرمزگان. چطور می‌توانم کمکتون کنم؟"
        
        elif intent == "location_query":
            # Extract location/service type from entities
            service_type = self._extract_service_type(nlp_result["entities"])
            
            if user_location and service_type:
                # Find nearest services
                nearby = self.location_service.find_nearest_services(
                    rag_result["retrieved_documents"],
                    user_location["latitude"],
                    user_location["longitude"],
                    service_type=service_type,
                    radius_km=5
                )
                
                if nearby:
                    response = f"نزدیکترین {service_type}:\n"
                    for service in nearby[:3]:
                        response += (
                            f"• {service.get('name')} - "
                            f"{service.get('distance_km')}کم فاصله\n"
                            f"  📞 {service.get('phone', 'موجود نیست')}\n"
                            f"  📍 {service.get('address', 'موجود نیست')}\n"
                        )
                else:
                    response = f"متأسفانه {service_type} نزدیک شما پیدا نشد."
            else:
                response = rag_result["response"]
        
        elif intent == "direction":
            if user_location and rag_result["retrieved_documents"]:
                destination = rag_result["retrieved_documents"][0]
                route_info = self.location_service.get_route_info(
                    user_location["latitude"],
                    user_location["longitude"],
                    destination["latitude"],
                    destination["longitude"],
                    destination
                )
                response = (
                    f"مسیر تا {destination.get('name')}:\n"
                    f"فاصله: {route_info['distance_km']} کیلومتر\n"
                    f"زمان برآورد شده: {route_info['estimated_time_minutes']} دقیقه\n"
                    f"آدرس: {destination.get('address', 'موجود نیست')}"
                )
            else:
                response = rag_result["response"]
        
        elif intent == "service_inquiry":
            response = rag_result["response"]
        
        else:
            response = rag_result["response"]
        
        return response
    
    def _extract_service_type(self, entities: List[Dict]) -> Optional[str]:
        """Extract service type from entities"""
        if not entities:
            return None
        
        service_types = {
            "بیمارستان": "hospital",
            "مدرسه": "school",
            "دانشگاه": "university",
            "بانک": "bank",
            "داروخانه": "pharmacy",
            "دفتر": "office",
        }
        
        for entity in entities:
            word = entity.get("word", "").lower()
            for farsi_term, service_type in service_types.items():
                if farsi_term in word:
                    return service_type
        
        return None
    
    def _save_chat_history(self, chat_result: Dict) -> None:
        """Save chat history to database"""
        try:
            # This would be implemented with actual database connection
            logger.info(f"💾 Saving chat history for user: {chat_result['user_id']}")
        except Exception as e:
            logger.error(f"Error saving chat history: {e}")
    
    def get_chat_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get chat history for a user"""
        logger.info(f"📖 Getting chat history for user: {user_id}")
        
        if not self.db_connection:
            logger.warning("Database connection not available")
            return []
        
        # This would be implemented with actual database query
        return []


# Global Chat Service Instance
chat_service = None

def get_chat_service(db_connection=None) -> ChatService:
    """Get or initialize chat service"""
    global chat_service
    if chat_service is None:
        chat_service = ChatService(db_connection)
    return chat_service
