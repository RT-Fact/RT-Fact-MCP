import os

from graph.state import PipelineSentence
from services.llm import GeminiService


async def verification_node(sentence: PipelineSentence) -> PipelineSentence:
    """
    Verification Node: claim 문장과 sources를 바탕으로 진실 여부를 판정합니다.
    GeminiService를 사용해 실제 LLM 호출
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    service = GeminiService(api_key=api_key)
    result = await service.verify_claim(
        claim=sentence["text"],
        sources=sentence.get("sources", []),
    )

    sentence["verdict"] = result["verdict"]
    sentence["suggestion"] = result.get("suggestion")

    return sentence
