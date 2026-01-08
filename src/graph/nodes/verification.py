from graph.state import PipelineSentence
from services.providers import get_gemini_service


async def verification_node(sentence: PipelineSentence) -> PipelineSentence:
    """
    Verification Node: claim 문장과 sources를 바탕으로 진실 여부를 판정합니다.
    GeminiService를 사용해 실제 LLM 호출 (싱글톤 인스턴스 사용)
    """
    service = get_gemini_service()
    result = await service.verify_claim(
        claim=sentence["text"],
        sources=sentence.get("sources", []),
    )

    sentence["verdict"] = result["verdict"]
    sentence["suggestion"] = result.get("suggestion")

    return sentence
