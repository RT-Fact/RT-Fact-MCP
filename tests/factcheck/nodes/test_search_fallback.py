from unittest.mock import AsyncMock, call, patch

import pytest

from factcheck.nodes.search import search_node
from factcheck.state import SentenceState


@pytest.fixture
def mock_tavily_service():
    with patch("factcheck.nodes.search.get_tavily_service") as mock_get:
        service_mock = AsyncMock()
        mock_get.return_value = service_mock
        yield service_mock


@pytest.mark.asyncio
async def test_search_node_whitelist_success(mock_tavily_service):
    """Scenario 1: Whitelist 검색 성공 -> 1회 호출 후 즉시 반환"""
    # Given
    sentence: SentenceState = {
        "text": "test query",
        "whitelist": ["trusted.com"],
        "blacklist": ["bad.com"],
        "type": "claim",
    }
    mock_tavily_service.search.return_value = [
        {"title": "Result 1", "url": "http://trusted.com/1", "snippet": "content"}
    ]

    # When
    result = await search_node(sentence)

    # Then
    mock_tavily_service.search.assert_awaited_once_with(
        query="test query",
        include_domains=["trusted.com"],
        exclude_domains=["bad.com"],
        max_results=3,
    )
    assert len(result.get("sources", [])) == 1


@pytest.mark.asyncio
async def test_search_node_fallback_execution(mock_tavily_service):
    """Scenario 2: Whitelist 실패(0건) -> Graylist 자동 재검색 (In-Node)"""
    # Given
    sentence: SentenceState = {
        "text": "test query",
        "whitelist": ["trusted.com"],
        "blacklist": ["bad.com"],
        "type": "claim",
    }

    # 순차적 반환 설정: 1차(빈 리스트) -> 2차(결과 있음)
    mock_tavily_service.search.side_effect = [
        [],
        [{"title": "Gray Result", "url": "http://other.com", "snippet": "content"}],
    ]

    # When
    result = await search_node(sentence)

    # Then
    assert mock_tavily_service.search.await_count == 2

    # 호출 순서 및 인자 검증
    expected_calls = [
        call(
            query="test query",
            include_domains=["trusted.com"],
            exclude_domains=["bad.com"],
            max_results=3,
        ),
        call(
            query="test query",
            include_domains=None,  # 2차는 Whitelist 해제
            exclude_domains=["bad.com"],
            max_results=3,
        ),
    ]
    mock_tavily_service.search.assert_has_awaits(expected_calls)

    sources = result.get("sources", [])
    assert len(sources) == 1
    assert sources[0]["title"] == "Gray Result"
