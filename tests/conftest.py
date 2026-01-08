"""pytest 공통 fixture 설정"""

import pytest

from services.providers import get_gemini_service, get_tavily_service


@pytest.fixture(autouse=True)
def clear_service_cache():
    """
    각 테스트 전후로 서비스 싱글톤 캐시를 초기화합니다.
    테스트 간 상태 격리를 보장합니다.
    """
    # 테스트 전: 캐시 초기화
    get_tavily_service.cache_clear()
    get_gemini_service.cache_clear()

    yield

    # 테스트 후: 캐시 초기화
    get_tavily_service.cache_clear()
    get_gemini_service.cache_clear()
