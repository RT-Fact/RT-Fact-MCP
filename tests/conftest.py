"""pytest 공통 fixture 설정"""

from unittest.mock import MagicMock, patch

import pytest

from services.llm import GeminiService
from services.providers import get_gemini_service, get_tavily_service
from services.search import TavilyService


@pytest.fixture(autouse=True)
def clear_service_cache():
    """
    각 테스트 전후로 서비스 싱글톤 캐시를 초기화합니다.
    테스트 간 상태 격리를 보장합니다.
    """
    get_tavily_service.cache_clear()
    get_gemini_service.cache_clear()

    yield

    get_tavily_service.cache_clear()
    get_gemini_service.cache_clear()


@pytest.fixture
def mock_gemini_service():
    """
    GeminiService mock fixture.
    extraction, verification 노드 테스트용.

    Usage:
        def test_something(mock_gemini_service):
            mock_gemini_service.extract_sentences = AsyncMock(return_value={...})
            mock_gemini_service.verify_claim = AsyncMock(return_value={...})
    """
    mock = MagicMock(spec=GeminiService)
    with (
        patch("factcheck.nodes.extraction.get_gemini_service", return_value=mock),
        patch("factcheck.nodes.verification.get_gemini_service", return_value=mock),
    ):
        yield mock


@pytest.fixture
def mock_tavily_service():
    """
    TavilyService mock fixture.
    search 노드 테스트용.

    Usage:
        def test_something(mock_tavily_service):
            mock_tavily_service.search = AsyncMock(return_value=[...])
    """
    mock = MagicMock(spec=TavilyService)
    with patch("factcheck.nodes.search.get_tavily_service", return_value=mock):
        yield mock
