"""Pytest Configuration"""

import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

@pytest.fixture(scope="session")
def test_config():
    """Test configuration"""
    return {
        "database_url": "sqlite:///:memory:",
        "debug": True,
    }

@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests"""
    yield
    # Reset after each test
    import app.core.nlp_engine as nlp_module
    import app.core.rag_pipeline as rag_module
    import app.core.location_service as location_module
    import app.services.chat_service as chat_module
    
    nlp_module.nlp_engine = None
    rag_module.rag_pipeline = None
    location_module.location_service = None
    chat_module.chat_service = None
