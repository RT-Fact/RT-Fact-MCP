from graph.state import PipelineSentence
from services.providers import get_tavily_service


async def search_node(sentence: PipelineSentence) -> PipelineSentence:
    """
    검색(Search)을 수행하는 노드입니다.
    claim 문장에 대해 TavilyService를 통해 관련 소스를 검색합니다.
    """

    service = get_tavily_service()

    search_strategies = [
        sentence.get("whitelist", []),
        None,
    ]

    sources = []
    for domains in search_strategies:
        sources = await service.search(
            query=sentence["text"],
            include_domains=domains,
            exclude_domains=sentence.get("blacklist", []),
            max_results=3,
        )

        if sources:
            break

    sentence["sources"] = sources

    return sentence
