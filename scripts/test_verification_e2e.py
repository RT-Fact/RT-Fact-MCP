"""E2E test for verification_node with real Gemini API"""

from dotenv import load_dotenv

load_dotenv()

import asyncio  # noqa: E402

from factcheck.nodes.verification import verification_node  # noqa: E402
from factcheck.state import SentenceState  # noqa: E402

"""사용법(터미널): PYTHONPATH=src poetry run python scripts/test_verification_e2e.py"""


async def test():
    # 테스트할 claim 문장들 (sources 포함)
    test_sentences: list[SentenceState] = [
        {
            "type": "claim",
            "text": "비트코인은 2009년에 출시되었다.",
            "start_index": 0,
            "end_index": 20,
            "retry_count": 0,
            "sources": [
                {
                    "title": "Bitcoin Wikipedia",
                    "url": "https://en.wikipedia.org/wiki/Bitcoin",
                    "snippet": "Bitcoin was released as open-source software in January 2009.",
                },
                {
                    "title": "사토시 나카모토",
                    "url": "https://ko.wikipedia.org/wiki/비트코인",
                    "snippet": "2009년 1월 3일에 첫 번째 블록(제네시스 블록)이 생성되었다.",
                },
            ],
        },
        {
            "type": "claim",
            "text": "비트코인은 2008년에 출시되었다.",  # FALSE expected
            "start_index": 21,
            "end_index": 40,
            "retry_count": 0,
            "sources": [
                {
                    "title": "Bitcoin History",
                    "url": "https://example.com/bitcoin",
                    "snippet": "Bitcoin was launched in January 2009 by Satoshi Nakamoto.",
                },
            ],
        },
        {
            "type": "claim",
            "text": "삼성전자는 1969년에 설립되었습니다.",
            "start_index": 41,
            "end_index": 60,
            "retry_count": 0,
            "sources": [
                {
                    "title": "삼성전자 공식 소개",
                    "url": "https://www.samsung.com/sec/aboutsamsung/",
                    "snippet": (
                        "1969년에 설립된 삼성전자는 대한민국 경기도 수원에 본사를 두고 있습니다."
                    ),
                },
            ],
        },
    ]

    print("=" * 60)
    print("Verification Node E2E Test (Real Gemini API)")
    print("=" * 60)

    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n[Test {i}] Claim: {sentence.get('text')}")
        print(f"  Sources: {len(sentence.get('sources', []))}개")
        print("-" * 40)

        try:
            result = await verification_node(sentence)

            verdict = result.get("verdict", "N/A")
            suggestion = result.get("suggestion")

            if verdict == "TRUE":
                print(f"  ✅ Verdict: {verdict}")
            else:
                print(f"  ❌ Verdict: {verdict}")
                if suggestion:
                    print(f"  💡 Suggestion: {suggestion}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    print()
    print("=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test())
