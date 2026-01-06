"""Search 단계 Mock 노드"""

from graph.state import FactCheckState


def search_node(state: FactCheckState) -> FactCheckState:
    """
    Search Node: 추출된 문장들에 대해 근거 자료를 검색 (Mock)
    """
    sentences = state.get("sentences", [])

    # [Mock Logic]
    # 실제로는 각 문장에 대해 검색 API를 호출해야 함
    updated_sentences = []
    for sent in sentences:
        new_sent = sent.copy()
        new_sent["evidence"] = [
            {
                "url": "https://trusted-news.com/article/1",
                "content": "This is a mock evidence supporting the claim.",
            }
        ]
        updated_sentences.append(new_sent)

    state["sentences"] = updated_sentences
    return state
