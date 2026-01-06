"""GeminiService Mock 테스트"""
import pytest
from unittest.mock import AsyncMock
from services import llm


@pytest.mark.asyncio
async def test_gemini_service_extract_sentences(mocker):
    """문장 추출 API 호출 테스트 (Mock)"""
    # Mock 준비
    mock_response = [
        {
            "type": "claim",
            "text": "테스트 문장입니다.",
            "startIndex": 0,
            "endIndex": 10
        }
    ]
    
    # GeminiService.extract_sentences Mock 처리
    mocker.patch.object(
        llm.GeminiService,
        "extract_sentences",
        new=AsyncMock(return_value=mock_response)
    )
    
    # 실행
    service = llm.GeminiService(api_key="test-key")
    result = await service.extract_sentences("테스트 텍스트")
    
    # 검증
    assert len(result) > 0
    assert result[0]["type"] == "claim"


@pytest.mark.asyncio
async def test_gemini_service_verify_claim(mocker):
    """Claim 검증 API 호출 테스트 (Mock)"""
    mock_response = {
        "verdict": "TRUE",
        "suggestion": None
    }
    
    mocker.patch.object(
        llm.GeminiService,
        "verify_claim",
        new=AsyncMock(return_value=mock_response)
    )
    
    service = llm.GeminiService(api_key="test-key")
    mock_sources = [
        {"title": "Example Source", "url": "https://example.com", "snippet": "관련 정보..."}
    ]
    result = await service.verify_claim("테스트 주장", mock_sources)
    
    assert result["verdict"] == "TRUE"
