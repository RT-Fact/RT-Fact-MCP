from factcheck.state import SentenceState
from services.providers import get_tavily_service


async def search_node(state: SentenceState) -> SentenceState:
    """
    검색(Search)을 수행하는 노드입니다.
    claim 문장에 대해 TavilyService를 통해 관련 소스를 검색합니다.
    """
    if "text" not in state:
        raise ValueError("search_node requires 'text' field in state")

    service = get_tavily_service()

    search_strategies = [
        state.get("whitelist", []),
        None,
    ]

    sources = []
    for domains in search_strategies:
        sources = await service.search(
            query=state["text"],
            include_domains=domains,
            exclude_domains=state.get("blacklist", []),
            max_results=3,
        )

        if sources:
            break

    state["sources"] = sources

    return state
