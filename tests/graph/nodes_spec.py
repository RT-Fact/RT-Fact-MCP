"""Mock 노드 단위 테스트"""

from unittest.mock import AsyncMock, patch

import pytest

from graph.nodes import extraction, search, verification
from graph.state import FactCheckState, PipelineSentence


@pytest.mark.asyncio
async def test_extraction_node():
    """Extraction 노드가 PipelineSentence를 잘 생성하는지 테스트"""
    initial_state: FactCheckState = {
        "original_text": "테스트 텍스트",
        "title": "",
        "sentences": [],
        "whitelist": [],
        "blacklist": [],
    }

    mock_result = {
        "title": "테스트 제목",
        "sentences": [
            {"type": "claim", "text": "테스트 문장입니다.", "startIndex": 0, "endIndex": 10}
        ],
    }

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
        with patch.object(
            extraction.GeminiService, "extract_sentences", new=AsyncMock(return_value=mock_result)
        ):
            new_state = await extraction.extraction_node(initial_state)

    assert len(new_state["sentences"]) > 0
    first_sent = new_state["sentences"][0]
    assert "type" in first_sent
    assert "text" in first_sent
    assert "startIndex" in first_sent


@pytest.mark.asyncio
async def test_search_node():
    """Search 노드가 검색을 수행하고 sources를 추가하는지 테스트"""
    # 초기 상태 (첫 진입)
    sentence: PipelineSentence = {
        "type": "claim",
        "text": "테스트 주장",
        "startIndex": 0,
        "endIndex": 5,
        "retry_count": 0,
    }

    mock_sources = [{"title": "Test", "url": "https://test.com", "snippet": "테스트 결과"}]

    with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}):
        with patch.object(search.TavilyService, "search", new=AsyncMock(return_value=mock_sources)):
            result = await search.search_node(sentence)

    assert "sources" in result
    assert len(result["sources"]) > 0
    assert result["retry_count"] == 0  # 첫 진입이므로 증가 안 함


@pytest.mark.asyncio
async def test_search_node_retry():
    """Search 노드가 재진입 시 retry_count를 증가시키는지 테스트"""
    # 재진입 상태 (이미 sources가 있음)
    sentence: PipelineSentence = {
        "type": "claim",
        "text": "테스트 주장",
        "startIndex": 0,
        "endIndex": 5,
        "retry_count": 0,
        "sources": [{"title": "Old", "url": "url", "snippet": "old"}],
    }

    mock_sources = [{"title": "New", "url": "https://new.com", "snippet": "새 결과"}]

    with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}):
        with patch.object(search.TavilyService, "search", new=AsyncMock(return_value=mock_sources)):
            result = await search.search_node(sentence)

    assert result["retry_count"] == 1  # 증가했어야 함
    assert "sources" in result  # 검색 다시 수행됨


@pytest.mark.asyncio
async def test_search_node_with_domain_filters():
    """Search 노드가 whitelist/blacklist를 TavilyService에 전달하는지 테스트"""
    sentence: PipelineSentence = {
        "type": "claim",
        "text": "테스트 주장",
        "startIndex": 0,
        "endIndex": 5,
        "retry_count": 0,
        "whitelist": ["trusted.com", "reliable.org"],
        "blacklist": ["spam.com"],
    }

    mock_sources = [{"title": "Test", "url": "https://trusted.com", "snippet": "결과"}]
    mock_search = AsyncMock(return_value=mock_sources)

    with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}):
        with patch.object(search.TavilyService, "search", mock_search):
            await search.search_node(sentence)

    # TavilyService.search()에 도메인 필터가 전달되었는지 확인
    mock_search.assert_called_once_with(
        query="테스트 주장",
        include_domains=["trusted.com", "reliable.org"],
        exclude_domains=["spam.com"],
        max_results=5,
    )


@pytest.mark.asyncio
async def test_verification_node_true():
    """Verification 노드가 TRUE verdict를 설정하는지 테스트"""
    sentence: PipelineSentence = {
        "type": "claim",
        "text": "테스트 주장",
        "startIndex": 0,
        "endIndex": 5,
        "sources": [{"title": "T", "url": "U", "snippet": "S"}],
        "retry_count": 0,
    }

    mock_result = {"verdict": "TRUE"}

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
        with patch.object(
            verification.GeminiService, "verify_claim", new=AsyncMock(return_value=mock_result)
        ):
            result = await verification.verification_node(sentence)

    assert result["verdict"] == "TRUE"
    assert result["suggestion"] is None


@pytest.mark.asyncio
async def test_verification_node_false_with_suggestion():
    """Verification 노드가 FALSE verdict와 suggestion을 설정하는지 테스트"""
    sentence: PipelineSentence = {
        "type": "claim",
        "text": "비트코인은 2008년에 출시되었다.",
        "startIndex": 0,
        "endIndex": 20,
        "sources": [{"title": "Bitcoin Wiki", "url": "https://...", "snippet": "2009년 출시..."}],
        "retry_count": 0,
    }

    mock_result = {"verdict": "FALSE", "suggestion": "비트코인은 2009년에 출시되었습니다."}

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
        with patch.object(
            verification.GeminiService, "verify_claim", new=AsyncMock(return_value=mock_result)
        ):
            result = await verification.verification_node(sentence)

    assert result["verdict"] == "FALSE"
    assert result["suggestion"] == "비트코인은 2009년에 출시되었습니다."
