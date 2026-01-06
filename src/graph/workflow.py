"""LangGraph 워크플로우 정의"""

from langgraph.graph import END, START, StateGraph

from graph.nodes import extraction, search, verification
from graph.state import FactCheckState


def create_factcheck_graph():
    """팩트체크 파이프라인 그래프 생성"""

    # 1. StateGraph 초기화
    workflow = StateGraph(FactCheckState)

    # 2. 노드 추가
    workflow.add_node("extraction", extraction.extraction_node)
    workflow.add_node("search", search.search_node)
    workflow.add_node("verification", verification.verification_node)

    # 3. 엣지 연결
    workflow.add_edge(START, "extraction")
    workflow.add_edge("extraction", "search")
    workflow.add_edge("search", "verification")
    workflow.add_edge("verification", END)

    return workflow.compile()
