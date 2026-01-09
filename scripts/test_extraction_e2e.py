"""E2E test for extraction_node with real Gemini API"""

from dotenv import load_dotenv

load_dotenv()

import asyncio  # noqa: E402

from graph.nodes.extraction import extraction_node  # noqa: E402

"""사용법(터미널): PYTHONPATH=src poetry run python scripts/test_extraction_e2e.py"""


async def test():
    # 약 500자 테스트 텍스트 (claim, opinion, excluded 혼합)
    original_text = (
        "대한민국의 수도는 서울이며, 인구는 약 970만 명입니다. "
        "서울은 정말 살기 좋은 도시입니다. "
        "2023년 한국의 GDP는 약 1조 7천억 달러로 세계 13위를 기록했습니다. "
        "우리나라 경제는 앞으로 더욱 성장할 것입니다. "
        "안녕하세요? "
        "삼성전자는 1969년에 설립되었으며 현재 세계 최대의 메모리 반도체 제조사입니다. "
        "애플이 삼성보다 더 혁신적이라고 생각합니다. "
        "비트코인은 2009년 사토시 나카모토에 의해 만들어졌습니다. "
        "암호화폐 투자는 신중하게 해야 합니다. "
        "오늘 날씨 어때요? "
        "한국어는 약 7천7백만 명이 사용하는 언어입니다. "
        "한국 음식은 세계에서 가장 맛있습니다."
    )

    state = {
        "original_text": original_text,
        "title": "",
        "sentences": [],
        "whitelist": [],
        "blacklist": [],
    }

    result = await extraction_node(state)

    print("Title:", result["title"])
    print("Original:", original_text)
    print()

    all_valid = True
    for s in result["sentences"]:
        type_str = s["type"]
        text_str = s["text"]
        start = s["start_index"]
        end = s["end_index"]

        # -1 인덱스 처리: LLM이 원본에서 문장을 찾지 못한 경우
        if start == -1:
            print(f"[{type_str}] {text_str}")
            print("  ⚠️ Sentence not found in original text (index: -1)")
            if "reason" in s:
                print(f"  reason: {s['reason']}")
            print()
            all_valid = False
            continue

        # 인덱스 검증: original_text[start:end]가 text와 일치하는지
        extracted = original_text[start:end]
        is_valid = extracted == text_str
        status = "✅" if is_valid else "❌"

        if not is_valid:
            all_valid = False

        print(f"[{type_str}] {text_str}")
        print(f"  indices: [{start}:{end}]")
        print(f"  extracted: '{extracted}' {status}")
        if "reason" in s:
            print(f"  reason: {s['reason']}")
        print()

    if all_valid:
        print("✅ All indices are correct!")
    else:
        print("❌ Some indices are incorrect!")


if __name__ == "__main__":
    asyncio.run(test())
