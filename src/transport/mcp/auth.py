"""MCP 도구 인증 모듈 - BE API Key 검증"""

from typing import Literal

import httpx

from config import get_settings

AuthResult = Literal["valid", "invalid", "error"]


async def validate_api_key(api_key: str) -> AuthResult:
    """
    Back-end API를 호출하여 API Key 유효성을 검증합니다.

    Args:
        api_key: 검증할 API Key (rtf_ prefix 포함)

    Returns:
        "valid": 유효한 키
        "invalid": 키 누락 또는 유효하지 않은 키
        "error": BE 장애 또는 네트워크 오류
    """
    if not api_key:
        return "invalid"

    settings = get_settings()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.backend_url}/api-keys/verify",
                json={"key": api_key},
                headers={"x-internal-secret": settings.internal_api_secret},
                timeout=5.0,
            )
        except httpx.HTTPError:
            return "error"

        if response.status_code != 200:
            return "error"

        try:
            data = response.json()
        except ValueError:
            return "error"

        if data.get("valid", False):
            return "valid"
        return "invalid"
