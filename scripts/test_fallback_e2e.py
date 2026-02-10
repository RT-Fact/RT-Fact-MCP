"""E2E test specific for Fallback Logic verification

사용법: PYTHONPATH=src poetry run python scripts/test_fallback_e2e.py
"""

import asyncio
from urllib.parse import urlparse

from dotenv import load_dotenv

from factcheck.pipeline import create_graph
from factcheck.state import SentenceState

_ = load_dotenv()


def extract_domain(url: str) -> str:
    """URL에서 도메인 추출"""
    try:
        return urlparse(url).netloc
    except Exception:
        return ""


async def test_fallback():
    """Fallback 로직 검증: Whitelist 실패 -> Graylist 자동 전환 확인"""

    # 1. 테스트 입력 (긴 텍스트)
    test_text = (
        "지구는 평평하다는 주장이 있습니다. 그러나 과학적으로 지구는 타원형의 구체입니다. "
        "물은 100도에서 끓습니다. "
        "아인슈타인은 상대성 이론을 발표했다. "
        "비타민 C는 감기를 예방한다고 알려져 있습니다. "
    )

    # 2. 강제 Fallback 유도 설정
    # 존재하지 않거나 정보가 없을 도메인만 Whitelist에 포함
    dummy_whitelist = ["example.com", "nonexistent-domain.xyz"]

    print(f"입력 텍스트: {test_text[:50]}...")
    print(f"설정된 Whitelist: {dummy_whitelist}")
    print(">>> 1차 검색(Whitelist)은 실패하고 자동으로 2차 검색(Graylist)이 수행되어야 합니다.\n")

    print("파이프라인 실행 중...")
    graph = create_graph()

    # LangGraph 실행
    result = await graph.ainvoke(
        {
            "original_text": test_text,
            "whitelist": dummy_whitelist,
            "blacklist": [],
            "title": "",
            "sentences": [],
        }
    )

    sentences: list[SentenceState] = result["sentences"]

    # 3. 결과 검증 및 출력
    print("\n[검증 결과]")

    claims = [s for s in sentences if s.get("type") == "claim"]
    fallback_success_count = 0

    for i, sent in enumerate(claims):
        print(f"\n--- Claim {i + 1} ---")
        print(f"텍스트: {sent.get('text')}")

        sources = sent.get("sources", [])
        print(f"검색된 소스 수: {len(sources)}")

        if not sources:
            print("❌ 검색 실패 (소스 없음)")
            continue

        # 소스 도메인 확인
        found_domains = {extract_domain(src["url"]) for src in sources}
        print(f"발견된 도메인: {found_domains}")

        # Whitelist에 없는 도메인이 발견되면 Fallback 성공으로 간주
        is_fallback_triggered = any(d not in dummy_whitelist for d in found_domains)

        if is_fallback_triggered:
            print("✅ Fallback 동작 확인됨 (Whitelist 외 도메인에서 검색됨)")
            fallback_success_count += 1
        else:
            print("❓ Whitelist 내에서만 검색됨 (Fallback 미발동 혹은 Whitelist 성공)")

    print(f"\n총 Claim 수: {len(claims)}")
    print(f"Fallback 성공 수: {fallback_success_count}")

    if fallback_success_count > 0:
        print("\nSUCCESS: Fallback 로직이 정상 동작했습니다.")
    else:
        print("\nFAIL: Fallback이 동작하지 않았거나 검색된 소스가 없습니다.")


if __name__ == "__main__":
    asyncio.run(test_fallback())
