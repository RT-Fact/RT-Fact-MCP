"""환경변수 설정 관리 - pydantic-settings 기반"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스.
    환경변수 또는 .env 파일에서 설정값을 로드합니다.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    gemini_api_key: str
    tavily_api_key: str
    gemini_model: str = "gemini-2.5-flash-lite"

    environment: Literal["dev", "prod"] = "dev"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Settings 싱글톤 인스턴스를 반환합니다.

    Returns:
        Settings: 캐시된 설정 인스턴스

    Raises:
        ValidationError: 필수 환경변수가 누락된 경우
    """
    return Settings()
