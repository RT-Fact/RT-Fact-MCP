from graph.state import PipelineSentence
from services.providers import get_tavily_service


async def search_node(sentence: PipelineSentence) -> PipelineSentence:
    """
    검색(Search)을 수행하는 노드입니다.
    claim 문장에 대해 TavilyService를 통해 관련 소스를 검색합니다.
    """

    service = get_tavily_service()

    # 1. 1차 검색 (Whitelist)
    sources = await service.search(
        query=sentence["text"],
        include_domains=sentence.get("whitelist", []),
        exclude_domains=sentence.get("blacklist", []),
        max_results=3,
    )

    if not sources:
        # 2. 2차 검색 (Fallback: Graylist) - 결과가 0건일 때
        sources = await service.search(
            query=sentence["text"],
            include_domains=None,  # Whitelist 해제
            exclude_domains=sentence.get("blacklist", []),
            max_results=3,
        )

    sentence["sources"] = sources

    return sentence
