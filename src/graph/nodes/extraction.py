from graph.state import FactCheckState


async def extraction_node(state: FactCheckState) -> FactCheckState:
    """
    Extraction Node: 텍스트에서 팩트체크가 필요한 문장을 추출 (Mock)
    """
    original_text = state.get("original_text", "")

    # ... 여기서 실제 LLM 호출 (지금은 Mock) ...
    # API 호출 대기 시간 시뮬레이션 (0초)

    # 더미 데이터 생성
    # PipelineSentence 구조에 맞춰 데이터 생성
    extracted_sentences = [
        {
            "type": "claim",
            "text": f"Extracted claim from: {original_text[:10]}...",
            "startIndex": 0,
            "endIndex": 10,
        },
        {
            "type": "opinion",
            "text": "This is an opinion statement.",
            "startIndex": 11,
            "endIndex": 20,
            "reason": "Contains subjective language."
        }
    ]

    return {
        "title": f"Topic: {original_text[:10]}...",
        "sentences": extracted_sentences
    }
