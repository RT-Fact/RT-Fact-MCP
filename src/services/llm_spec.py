"""GeminiService Mock 테스트"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from services import llm


@pytest.mark.asyncio
async def test_gemini_service_extract_sentences(mocker):
    """문장 추출 API 호출 테스트 (Mock) - 반환 타입 일치 확인"""
    # Mock 준비 - 실제 반환 형식과 일치
    mock_response = {
        "title": "테스트 제목",
        "sentences": [
            {"type": "claim", "text": "테스트 문장입니다.", "start_index": 0, "end_index": 10}
        ],
    }

    # GeminiService.extract_sentences Mock 처리
    mocker.patch.object(
        llm.GeminiService, "extract_sentences", new=AsyncMock(return_value=mock_response)
    )

    # 실행
    service = llm.GeminiService(api_key="test-key")
    result = await service.extract_sentences("테스트 텍스트")

    # 검증 - 실제 반환 구조에 맞게 수정
    assert result["title"] == "테스트 제목"
    assert len(result["sentences"]) > 0
    assert result["sentences"][0]["type"] == "claim"


@pytest.mark.asyncio
async def test_gemini_service_verify_claim(mocker):
    """Claim 검증 API 호출 테스트 (Mock)"""
    mock_response = {"verdict": "TRUE", "suggestion": None}

    mocker.patch.object(
        llm.GeminiService, "verify_claim", new=AsyncMock(return_value=mock_response)
    )

    service = llm.GeminiService(api_key="test-key")
    mock_sources = [
        {"title": "Example Source", "url": "https://example.com", "snippet": "관련 정보..."}
    ]
    result = await service.verify_claim("테스트 주장", mock_sources)

    assert result["verdict"] == "TRUE"


@pytest.mark.asyncio
async def test_verify_claim_true_verdict(mocker):
    """TRUE 판정 시 suggestion이 None인지 테스트"""
    mock_llm_result = llm.VerificationResult(verdict="TRUE", suggestion=None)

    mock_api_response = MagicMock()
    mock_api_response.text = mock_llm_result.model_dump_json()

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_api_response)
    mocker.patch.object(llm.genai, "Client", return_value=mock_client)

    service = llm.GeminiService(api_key="test-key")
    result = await service.verify_claim(
        claim="서울은 대한민국의 수도이다.",
        sources=[
            {"title": "Wikipedia", "url": "https://...", "snippet": "서울은 대한민국의 수도..."}
        ],
    )

    assert result["verdict"] == "TRUE"
    assert "suggestion" not in result  # exclude_none=True이므로 None은 제외됨


@pytest.mark.asyncio
async def test_verify_claim_false_verdict_with_suggestion(mocker):
    """FALSE 판정 시 suggestion이 포함되는지 테스트"""
    mock_llm_result = llm.VerificationResult(
        verdict="FALSE", suggestion="비트코인은 2008년이 아닌 2009년에 출시되었습니다."
    )

    mock_api_response = MagicMock()
    mock_api_response.text = mock_llm_result.model_dump_json()

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_api_response)
    mocker.patch.object(llm.genai, "Client", return_value=mock_client)

    service = llm.GeminiService(api_key="test-key")
    result = await service.verify_claim(
        claim="비트코인은 2008년에 출시되었다.",
        sources=[
            {"title": "Bitcoin Wiki", "url": "https://...", "snippet": "2009년 1월에 출시..."}
        ],
    )

    assert result["verdict"] == "FALSE"
    assert result["suggestion"] == "비트코인은 2008년이 아닌 2009년에 출시되었습니다."


@pytest.mark.asyncio
async def test_extract_sentences_index_calculation(mocker):
    """인덱스 계산 로직 테스트 - 원본 텍스트에서 문장 위치 정확도"""
    # 원본 텍스트
    original_text = "첫 번째 문장입니다. 두 번째 문장입니다."

    # LLM 응답 Mock (인덱스 없음 - 실제 LLM 응답처럼)
    mock_llm_result = llm.ExtractionResult(
        title="테스트",
        sentences=[
            llm.ExtractedSentence(type="claim", text="첫 번째 문장입니다."),
            llm.ExtractedSentence(type="claim", text="두 번째 문장입니다."),
        ],
    )

    # Gemini API 응답 Mock
    mock_api_response = MagicMock()
    mock_api_response.text = mock_llm_result.model_dump_json()

    # Client Mock
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_api_response)
    mocker.patch.object(llm.genai, "Client", return_value=mock_client)

    # 실행
    service = llm.GeminiService(api_key="test-key")
    result = await service.extract_sentences(original_text)

    # 검증 - 인덱스가 정확히 계산되었는지
    assert result["sentences"][0]["start_index"] == 0
    assert result["sentences"][0]["end_index"] == 11  # "첫 번째 문장입니다." 길이
    assert result["sentences"][1]["start_index"] == 12  # 공백 포함
    assert result["sentences"][1]["end_index"] == 23  # "두 번째 문장입니다." 끝


@pytest.mark.asyncio
async def test_extract_sentences_duplicate_handling(mocker):
    """중복 문장 처리 테스트 - 같은 문장이 2번 나올 때 각각 다른 인덱스"""
    # 같은 문장이 두 번 나오는 텍스트
    original_text = "안녕하세요. 반갑습니다. 안녕하세요."

    mock_llm_result = llm.ExtractionResult(
        title="인사",
        sentences=[
            llm.ExtractedSentence(type="excluded", text="안녕하세요.", reason="인사말"),
            llm.ExtractedSentence(type="excluded", text="반갑습니다.", reason="인사말"),
            llm.ExtractedSentence(type="excluded", text="안녕하세요.", reason="인사말"),
        ],
    )

    mock_api_response = MagicMock()
    mock_api_response.text = mock_llm_result.model_dump_json()

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_api_response)
    mocker.patch.object(llm.genai, "Client", return_value=mock_client)

    # 실행
    service = llm.GeminiService(api_key="test-key")
    result = await service.extract_sentences(original_text)

    # 검증 - 첫 번째 "안녕하세요"와 두 번째 "안녕하세요"의 인덱스가 다름
    assert result["sentences"][0]["start_index"] == 0  # 첫 번째 "안녕하세요."
    assert result["sentences"][0]["end_index"] == 6
    assert result["sentences"][2]["start_index"] == 14  # 두 번째 "안녕하세요."
    assert result["sentences"][2]["end_index"] == 20


@pytest.mark.asyncio
async def test_extract_sentences_not_found_in_text(mocker):
    """문장을 원본에서 찾지 못할 때 -1 반환 테스트"""
    original_text = "원본 텍스트입니다."

    # LLM이 원본에 없는 문장을 반환하는 경우 (할루시네이션)
    mock_llm_result = llm.ExtractionResult(
        title="테스트",
        sentences=[
            llm.ExtractedSentence(type="claim", text="존재하지 않는 문장"),
        ],
    )

    mock_api_response = MagicMock()
    mock_api_response.text = mock_llm_result.model_dump_json()

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_api_response)
    mocker.patch.object(llm.genai, "Client", return_value=mock_client)

    # 실행
    service = llm.GeminiService(api_key="test-key")
    result = await service.extract_sentences(original_text)

    # 검증 - 찾지 못한 경우 -1
    assert result["sentences"][0]["start_index"] == -1
    assert result["sentences"][0]["end_index"] == -1


@pytest.mark.asyncio
async def test_extract_sentences_api_error(mocker):
    """API 호출 실패 시 예외 전파 테스트"""
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(
        side_effect=Exception("API rate limit exceeded")
    )
    mocker.patch.object(llm.genai, "Client", return_value=mock_client)

    service = llm.GeminiService(api_key="test-key")

    # 예외가 전파되는지 확인
    with pytest.raises(Exception) as exc_info:
        await service.extract_sentences("테스트")

    assert "rate limit" in str(exc_info.value)
