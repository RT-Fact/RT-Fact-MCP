"""Mock 노드 단위 테스트"""

from graph.nodes import extraction, search, verification
from graph.state import FactCheckState


def test_extraction_node():
    """Extraction 노드가 문장을 생성하는지 테스트"""
    initial_state: FactCheckState = {
        "original_text": "테스트 텍스트",
        "whitelist": [],
        "blacklist": [],
        "title": "",
        "sentences": [],
    }

    new_state = extraction.extraction_node(initial_state)

    assert new_state["title"].startswith("Topic:")
    assert len(new_state["sentences"]) > 0
    assert "claim" in new_state["sentences"][0]


def test_search_node():
    """Search 노드가 증거(evidence)를 추가하는지 테스트"""
    state: FactCheckState = {
        "original_text": "테스트",
        "whitelist": [],
        "blacklist": [],
        "title": "Test",
        "sentences": [{"claim": "테스트 주장"}],
    }

    new_state = search.search_node(state)

    assert "evidence" in new_state["sentences"][0]
    assert isinstance(new_state["sentences"][0]["evidence"], list)
    assert new_state["sentences"][0]["evidence"][0]["content"] == (
        "This is a mock evidence supporting the claim."
    )


def test_verification_node():
    """Verification 노드가 판정 결과(result)를 추가하는지 테스트"""
    state: FactCheckState = {
        "original_text": "테스트",
        "whitelist": [],
        "blacklist": [],
        "title": "Test",
        "sentences": [{"claim": "테스트 주장", "evidence": "테스트 증거"}],
    }

    new_state = verification.verification_node(state)

    item = new_state["sentences"][0]
    assert "verification_result" in item
    assert item["verification_result"]["label"] in ["True", "False", "Unverified"]
    assert "reasoning" in item["verification_result"]
