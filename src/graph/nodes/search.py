import os

from graph.state import PipelineSentence
from services.search import TavilyService


async def search_node(sentence: PipelineSentence) -> PipelineSentence:
    """
    검색(Search)을 수행하는 노드입니다.
    claim 문장에 대해 TavilyService를 통해 관련 소스를 검색합니다.
    """

    # 1. retry_count 증가 (재검색인 경우)
    if "retry_count" in sentence:
        # sources가 이미 채워져 있으면 재시도임
        if "sources" in sentence and sentence["sources"]:
            sentence["retry_count"] += 1

    # 2. TavilyService를 통한 검색 수행
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is required")

    service = TavilyService(api_key=api_key)
    sources = await service.search(
        query=sentence["text"],
        include_domains=sentence.get("whitelist", []),
        exclude_domains=sentence.get("blacklist", []),
        max_results=5,
    )

    sentence["sources"] = sources

    return sentence
