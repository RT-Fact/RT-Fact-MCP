from factcheck.state import SentenceState
from services.providers import get_gemini_service


async def verification_node(state: SentenceState) -> SentenceState:
    """
    Verification Node: claim 문장과 sources를 바탕으로 진실 여부를 판정합니다.
    GeminiService를 사용해 실제 LLM 호출 (싱글톤 인스턴스 사용)
    """
    if "text" not in state:
        raise ValueError("verification_node requires 'text' field in state")

    service = get_gemini_service()
    result = await service.verify_claim(
        claim=state["text"],
        sources=state.get("sources", []),
    )

    state["verdict"] = result["verdict"]
    state["suggestion"] = result.get("suggestion")

    # 검증 실패(FALSE) 시 재시도 횟수 증가 (Loop 종료 조건용)
    if state["verdict"] == "FALSE":
        state["retry_count"] = state.get("retry_count", 0) + 1

    return state
