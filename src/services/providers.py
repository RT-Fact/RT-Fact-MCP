"""Service Provider 함수들 - 싱글톤 패턴으로 서비스 인스턴스 제공"""

from functools import lru_cache

from config import get_settings
from services.llm import GeminiService
from services.search import TavilyService


@lru_cache(maxsize=1)
def get_tavily_service() -> TavilyService:
    """
    TavilyService 싱글톤 인스턴스를 반환합니다.

    Returns:
        TavilyService: 캐시된 서비스 인스턴스
    """
    settings = get_settings()
    return TavilyService(api_key=settings.tavily_api_key)


@lru_cache(maxsize=1)
def get_gemini_service() -> GeminiService:
    """
    GeminiService 싱글톤 인스턴스를 반환합니다.

    Returns:
        GeminiService: 캐시된 서비스 인스턴스
    """
    settings = get_settings()
    return GeminiService(api_key=settings.gemini_api_key)
