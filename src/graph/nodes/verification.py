"""Verification 단계 Mock 노드"""

from graph.state import FactCheckState


def verification_node(state: FactCheckState) -> FactCheckState:
    """
    Verification Node: 검색된 증거와 주장을 비교하여 검증 (Mock)
    """
    sentences = state.get("sentences", [])

    updated_sentences = []
    for sent in sentences:
        new_sent = sent.copy()
        evidence = new_sent.get("evidence", [])

        # [Mock Logic]
        # LLM을 호출하여 검증 수행
        new_sent["verification_result"] = {
            "label": "True" if evidence else "Unverified",
            "confidence": 0.95,
            "reasoning": "Based on the mock evidence provided.",
        }
        updated_sentences.append(new_sent)

    state["sentences"] = updated_sentences
    return state
