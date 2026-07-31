"""Unit Tests for Chat Service"""

import pytest
from app.services.chat_service import ChatService, get_chat_service

class TestChatService:
    """Tests for Chat Service"""
    
    @pytest.fixture
    def chat_service(self):
        """Initialize chat service for tests"""
        return ChatService()
    
    def test_process_greeting(self, chat_service):
        """Test processing greeting message"""
        result = chat_service.process_message(
            "سلام!",
            "user123"
        )
        
        assert result["user_id"] == "user123"
        assert result["message"] == "سلام!"
        assert result["intent"] == "greeting"
        assert len(result["response"]) > 0
    
    def test_process_location_query(self, chat_service):
        """Test processing location query"""
        result = chat_service.process_message(
            "نزدیک‌ترین بیمارستان کجاست؟",
            "user123"
        )
        
        assert result["intent"] == "location_query"
        assert len(result["response"]) > 0
    
    def test_process_with_location(self, chat_service):
        """Test processing with user location"""
        user_location = {
            "latitude": 27.2158,
            "longitude": 56.2808,
        }
        
        result = chat_service.process_message(
            "نزدیک‌ترین بیمارستان کجاست؟",
            "user123",
            user_location
        )
        
        assert "response" in result
        assert len(result["response"]) > 0
    
    def test_process_returns_timestamp(self, chat_service):
        """Test that processing returns timestamp"""
        result = chat_service.process_message(
            "سلام!",
            "user123"
        )
        
        assert "timestamp" in result
        assert len(result["timestamp"]) > 0
    
    def test_extract_service_type(self, chat_service):
        """Test service type extraction"""
        entities = [
            {"word": "بیمارستان"},
        ]
        
        service_type = chat_service._extract_service_type(entities)
        assert service_type == "hospital"
    
    def test_extract_service_type_university(self, chat_service):
        """Test service type extraction for university"""
        entities = [
            {"word": "دانش��اه"},
        ]
        
        service_type = chat_service._extract_service_type(entities)
        assert service_type == "university"
    
    def test_get_chat_history(self, chat_service):
        """Test getting chat history"""
        history = chat_service.get_chat_history("user123", limit=50)
        assert isinstance(history, list)
    
    def test_get_chat_service_singleton(self):
        """Test chat service singleton pattern"""
        service1 = get_chat_service()
        service2 = get_chat_service()
        assert service1 is service2


class TestChatServiceEdgeCases:
    """Edge case tests for chat service"""
    
    @pytest.fixture
    def chat_service(self):
        return ChatService()
    
    def test_process_empty_message(self, chat_service):
        """Test processing empty message"""
        result = chat_service.process_message(
            "",
            "user123"
        )
        
        assert "response" in result
    
    def test_process_long_message(self, chat_service):
        """Test processing very long message"""
        long_message = "سلام " * 100
        result = chat_service.process_message(
            long_message,
            "user123"
        )
        
        assert "response" in result
    
    def test_process_special_characters(self, chat_service):
        """Test processing message with special characters"""
        result = chat_service.process_message(
            "سلام!!! ؟؟؟ ...",
            "user123"
        )
        
        assert "response" in result
    
    def test_extract_service_type_none(self, chat_service):
        """Test service type extraction with no entities"""
        service_type = chat_service._extract_service_type([])
        assert service_type is None
    
    def test_extract_service_type_unknown(self, chat_service):
        """Test service type extraction with unknown entity"""
        entities = [
            {"word": "نامشخص"},
        ]
        
        service_type = chat_service._extract_service_type(entities)
        assert service_type is None
