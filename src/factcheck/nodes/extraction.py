from factcheck.state import ExtractionState, FactCheckState
from services.providers import get_gemini_service


async def extraction_node(state: FactCheckState) -> ExtractionState:
    """
    Extraction Node: 텍스트에서 팩트체크가 필요한 문장을 추출
    GeminiService를 사용해 실제 LLM 호출 (싱글톤 인스턴스 사용)
    """
    original_text = state.get("original_text", "")

    service = get_gemini_service()
    result = await service.extract_sentences(original_text)

    return {"title": result["title"], "sentences": result["sentences"]}
