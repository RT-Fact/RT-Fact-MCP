"""LangGraph 워크플로우 통합 테스트 (Mock)"""

import pytest

from graph.workflow import create_factcheck_graph


@pytest.mark.asyncio  # LangGraph 실행은 내부적으로 비동기일 수 있으므로 유지
async def test_full_pipeline_mock():
    """전체 파이프라인 실행 테스트 (Mock)"""

    # 1. 그래프 생성
    app = create_factcheck_graph()

    # 2. 초기 입력
    inputs = {"original_text": "한국의 수도는 서울이다.", "whitelist": [], "blacklist": []}

    # 3. 실행 (invoke 사용가능하지만, 테스트 환경에선 ainvoke 권장됨.
    # 하지만 사용자가 완전 롤백을 원했으므로 원래 코드 형태인 create_graph() 시절 로직 참고)
    # LangGraph 앱은 동기 노드로 구성되어도 비동기 실행이 가능함.
    final_state = await app.ainvoke(inputs)

    # 4. 검증
    # - Extraction 완료 확인
    assert final_state["title"].startswith("Topic:")
    assert len(final_state["sentences"]) == 1

    # - Search 결과 확인
    assert "evidence" in final_state["sentences"][0]

    # - Verification 결과 확인
    assert "verification_result" in final_state["sentences"][0]
