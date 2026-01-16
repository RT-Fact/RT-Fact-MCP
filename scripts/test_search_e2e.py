"""E2E test for search_node with real Tavily API"""

from dotenv import load_dotenv

load_dotenv()

import asyncio  # noqa: E402

from factcheck.nodes.search import search_node  # noqa: E402
from factcheck.state import SentenceState  # noqa: E402

"""사용법(터미널): PYTHONPATH=src poetry run python scripts/test_search_e2e.py"""


async def test():
    # 테스트할 claim 문장들
    test_sentences: list[SentenceState] = [
        {
            "type": "claim",
            "text": "비트코인은 2009년 사토시 나카모토에 의해 만들어졌습니다.",
            "start_index": 0,
            "end_index": 30,
            "retry_count": 0,
            "whitelist": [],
            "blacklist": [],
        },
        {
            "type": "claim",
            "text": "삼성전자는 1969년에 설립되었습니다.",
            "start_index": 31,
            "end_index": 50,
            "retry_count": 0,
            "whitelist": ["samsung.com"],  # whitelist 테스트
            "blacklist": ["wikipedia.org"],  # blacklist 테스트
        },
        {
            "type": "claim",
            "text": "한국의 GDP는 세계 13위입니다.",
            "start_index": 51,
            "end_index": 70,
            "retry_count": 0,
            "whitelist": [],
            "blacklist": [],
        },
    ]

    print("=" * 60)
    print("Search Node E2E Test (Real Tavily API)")
    print("=" * 60)

    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n[Test {i}] Query: {sentence.get('text')}")
        if sentence.get("whitelist"):
            print(f"  whitelist: {sentence.get('whitelist')}")
        if sentence.get("blacklist"):
            print(f"  blacklist: {sentence.get('blacklist')}")
        print("-" * 40)

        try:
            result = await search_node(sentence)

            sources = result.get("sources", [])
            print(f"  ✅ Found {len(sources)} sources:")
            for j, source in enumerate(sources, 1):
                print(f"     {j}. {source['title']}")
                print(f"        URL: {source['url']}")
                print(f"        Snippet: {source['snippet'][:100]}...")
                print()

        except Exception as e:
            print(f"  ❌ Error: {e}")

    print("=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test())
