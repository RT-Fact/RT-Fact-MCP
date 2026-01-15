"""E2E test for full factcheck pipeline with real APIs

사용법: PYTHONPATH=src poetry run python scripts/test_pipeline_e2e.py
"""

from dotenv import load_dotenv

_ = load_dotenv()

import asyncio  # noqa: E402

from graph.state import SentenceState  # noqa: E402
from graph.workflow import create_graph  # noqa: E402


async def test():
    """E2E 테스트: 전체 파이프라인 실행 및 응답 구조 검증"""

    # 1. 테스트 입력
    test_text = (
        "대한민국의 수도는 서울이다. "
        "서울의 인구는 약 1000만 명이다. "
        "한강은 서울을 가로지르는 강이다. "
        "서울은 정말 살기 좋은 도시라고 생각한다. "
        "지구는 태양계에서 세 번째 행성이다. "
        "아인슈타인은 상대성 이론을 발표했다. "
        "커피는 세상에서 가장 맛있는 음료이다."
    )
    print(f"입력: {test_text}\n")

    # 2. 파이프라인 실행
    print("파이프라인 실행 중...")
    graph = create_graph()
    result = await graph.ainvoke(
        {
            "original_text": test_text,
            "whitelist": [],
            "blacklist": [],
            "title": "",
            "sentences": [],
        }
    )

    # 3. 구조 검증 (assertion) - LangGraph State는 snake_case
    assert "title" in result, "title 필드 누락"
    assert "original_text" in result, "original_text 필드 누락"
    assert "sentences" in result, "sentences 필드 누락"
    assert len(result["sentences"]) >= 1, "최소 1개 문장 필요"

    # 4. 기본 정보 출력
    # LangGraph ainvoke 반환 타입이 dict[str, Any]이므로 명시적 타입 변환
    title: str = result["title"]
    original_text: str = result["original_text"]
    sentences: list[SentenceState] = result["sentences"]

    print(f"✓ 제목: {title}")
    print(f"✓ 원문: {original_text}")
    print(f"✓ 문장 수: {len(sentences)}")

    # 5. 각 문장 검증 + 출력
    # Note: 현재 LangGraph add Reducer로 인해 sentences에
    # extraction 단계(verdict 없음) + processing 단계(verdict 있음) claim이 공존할 수 있음.
    # 향후 리팩토링 시 processing 결과만 남도록 개선 예정.
    # 이 테스트는 두 경우 모두 통과하도록 작성됨.

    verified_claim_count = 0

    # 최종 결과만 필터링: opinion + verdict가 있는 claim
    final_sentences = [
        s
        for s in sentences
        if s.get("type") == "opinion" or (s.get("type") == "claim" and s.get("verdict") is not None)
    ]

    for i, sentence in enumerate(final_sentences):
        print(f"\n--- 문장 {i + 1} ---")

        sentence_type = sentence.get("type")
        sentence_text = sentence.get("text")

        assert sentence_type in ["claim", "opinion", "excluded"], f"잘못된 타입: {sentence_type}"
        print(f"타입: {sentence_type}")
        print(f"텍스트: {sentence_text}")

        if sentence_type == "claim":
            verdict = sentence.get("verdict")

            assert verdict in ["TRUE", "FALSE"], f"잘못된 verdict: {verdict}"
            assert "sources" in sentence, "sources 필드 누락"

            sources = sentence.get("sources", [])
            suggestion = sentence.get("suggestion")

            print(f"판정: {verdict}")
            print(f"출처 수: {len(sources)}")
            if suggestion:
                print(f"수정제안: {suggestion}")

            verified_claim_count += 1

        elif sentence_type == "opinion":
            reason = sentence.get("reason")
            assert reason is not None, "reason 필드 누락"
            print(f"이유: {reason}")

    assert verified_claim_count >= 1, (
        f"검증된 claim이 없음 (verified_claim_count={verified_claim_count})"
    )

    print(f"\n✓ 검증된 claim 수: {verified_claim_count}")
    print("\n✅ E2E 테스트 통과!")


if __name__ == "__main__":
    asyncio.run(test())
