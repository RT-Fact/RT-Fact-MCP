"""LangGraph 워크플로우 정의"""

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from graph.nodes.extraction import extraction_node
from graph.nodes.search import search_node
from graph.nodes.verification import verification_node
from graph.state import FactCheckState, SentenceState


def continue_to_processing(state: FactCheckState):
    """
    [Conditional Edge]
    Extraction 결과를 병렬 처리 SubGraph로 분배(Map)합니다.
    단, 'type'이 'claim'인 문장만 처리 대상으로 선정합니다.
    """
    start_nodes = []
    whitelist = state.get("whitelist", [])
    blacklist = state.get("blacklist", [])

    for s in state["sentences"]:
        if s.get("type") == "claim":
            # retry_count 초기화
            if "retry_count" not in s:
                s["retry_count"] = 0
            # whitelist/blacklist 전달
            s["whitelist"] = whitelist
            s["blacklist"] = blacklist
            start_nodes.append(Send("processing_node", s))

    return start_nodes


def check_verification_result(state: SentenceState):
    """
    [Conditional Edge for SubGraph]
    검증 결과가 FALSE이고 재시도 횟수가 남았으면 Search로 루프(Loop)
    """
    MAX_RETRIES = 1

    if state.get("verdict") == "FALSE":
        current_retries = state.get("retry_count", 0)
        if current_retries < MAX_RETRIES:
            # retry_count 증가는 여기서 할 수 없으므로(상태 변경 불가),
            # search_node에서 수행하거나 별도 노드가 필요함.
            # 여기서는 편의상 "search_node"가 retry_count를 보고 증가시킨다고 가정.
            return "search"

    return END


def create_processing_subgraph():
    """문장 처리용 SubGraph 생성 (Search -> Verify -> Loop)"""
    workflow = StateGraph(SentenceState)

    workflow.add_node("search", search_node)
    workflow.add_node("verification", verification_node)

    workflow.add_edge(START, "search")
    workflow.add_edge("search", "verification")

    workflow.add_conditional_edges(
        "verification", check_verification_result, {"search": "search", END: END}
    )

    return workflow.compile()


async def processing_node(state: SentenceState):
    """
    SubGraph를 실행하고 결과를 Main Graph의 Reducer 형식에 맞게 반환하는 래퍼 노드
    """
    processor = create_processing_subgraph()
    result = await processor.ainvoke(state)
    # result는 SentenceState (SubGraph의 최종 State)
    return {"sentences": [result]}


def create_graph():
    """전체 메인 워크플로우 생성"""
    graph_builder = StateGraph(FactCheckState)

    # 1. 노드 추가
    graph_builder.add_node("extraction", extraction_node)

    # SubGraph를 감싼 래퍼 노드 추가
    graph_builder.add_node("processing_node", processing_node)

    # 2. 엣지 연결
    graph_builder.add_edge(START, "extraction")

    # Extraction -> (Map) -> Processing Wrapper
    graph_builder.add_conditional_edges("extraction", continue_to_processing, ["processing_node"])

    return graph_builder.compile()
