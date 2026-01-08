"""Service Provider 함수들 - 싱글톤 패턴으로 서비스 인스턴스 제공"""

import os
from functools import lru_cache

from services.llm import GeminiService
from services.search import TavilyService


@lru_cache(maxsize=1)
def get_tavily_service() -> TavilyService:
    """
    TavilyService 싱글톤 인스턴스를 반환합니다.

    Returns:
        TavilyService: 캐시된 서비스 인스턴스

    Raises:
        ValueError: TAVILY_API_KEY 환경변수가 없는 경우
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is required")
    return TavilyService(api_key=api_key)


@lru_cache(maxsize=1)
def get_gemini_service() -> GeminiService:
    """
    GeminiService 싱글톤 인스턴스를 반환합니다.

    Returns:
        GeminiService: 캐시된 서비스 인스턴스

    Raises:
        ValueError: GEMINI_API_KEY 환경변수가 없는 경우
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    return GeminiService(api_key=api_key)
