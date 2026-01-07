"""Mock 노드 단위 테스트"""

import pytest
from unittest.mock import AsyncMock, patch

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
            {
                "type": "claim",
                "text": "테스트 문장입니다.",
                "startIndex": 0,
                "endIndex": 10
            }
        ]
    }

    with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
        with patch.object(
            extraction.GeminiService,
            "extract_sentences",
            new=AsyncMock(return_value=mock_result)
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
        "retry_count": 0
    }

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
        "sources": [{"title": "Old", "url": "url", "snippet": "old"}]
    }

    result = await search.search_node(sentence)

    assert result["retry_count"] == 1  # 증가했어야 함
    assert "sources" in result # 검색 다시 수행됨


@pytest.mark.asyncio
async def test_verification_node():
    """Verification 노드가 verdict를 설정하는지 테스트"""
    sentence: PipelineSentence = {
        "type": "claim",
        "text": "테스트 주장",
        "startIndex": 0,
        "endIndex": 5,
        "sources": [{"title": "T", "url": "U", "snippet": "S"}],
        "retry_count": 0
    }

    # retry_count가 0이면 Mock 로직상 FALSE
    result_false = await verification.verification_node(sentence)
    assert result_false["verdict"] == "FALSE"
    
    # retry_count가 1이면 Mock 로직상 TRUE
    sentence["retry_count"] = 1
    result_true = await verification.verification_node(sentence)
    assert result_true["verdict"] == "TRUE"
