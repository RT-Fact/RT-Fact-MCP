"""Extraction 단계 Mock 노드"""

from graph.state import FactCheckState


def extraction_node(state: FactCheckState) -> FactCheckState:
    """
    Extraction Node: 텍스트에서 팩트체크가 필요한 문장을 추출 (Mock)
    """
    original_text = state.get("original_text", "")

    # [Mock Logic]
    # 실제로는 LLM을 호출하여 중요 주장을 추출해야 함

    state["title"] = f"Topic: {original_text[:15]}..."
    state["sentences"] = [
        {
            "id": 1,
            "claim": original_text,  # 간단히 전체를 하나의 claim으로 간주
            "status": "extracted",
        }
    ]

    return state
