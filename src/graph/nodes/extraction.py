import os
from graph.state import FactCheckState
from services.llm import GeminiService


async def extraction_node(state: FactCheckState) -> FactCheckState:
    """
    Extraction Node: 텍스트에서 팩트체크가 필요한 문장을 추출
    GeminiService를 사용해 실제 LLM 호출
    """
    original_text = state.get("original_text", "")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    
    service = GeminiService(api_key=api_key)
    result = await service.extract_sentences(original_text)
    
    return {
        "title": result["title"],
        "sentences": result["sentences"]
    }
