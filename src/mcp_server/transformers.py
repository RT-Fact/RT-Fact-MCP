"""
Pipeline 결과 → MCP 응답 변환기

책임: 파이프라인 내부 데이터를 외부 API 형식으로 변환
- 내부 필드 제거 (retry_count, whitelist, blacklist)
- excluded 타입 문장 제외
- JSON 직렬화
"""

import json

from graph.state import FactCheckState, SentenceState
from mcp_server.schemas.tools.factcheck import (
    ClaimSentence,
    FactcheckResult,
    OpinionSentence,
    ResultSentence,
)


def transform_claim(sentence: SentenceState) -> ClaimSentence:
    """claim 문장을 MCP 응답 형식으로 변환."""
    return {
        "type": "claim",
        "text": sentence.get("text", ""),
        "startIndex": sentence.get("start_index", -1),
        "endIndex": sentence.get("end_index", -1),
        "verdict": sentence.get("verdict", "FALSE"),
        "sources": sentence.get("sources", []),
        "suggestion": sentence.get("suggestion"),
    }


def transform_opinion(sentence: SentenceState) -> OpinionSentence:
    """opinion 문장을 MCP 응답 형식으로 변환."""
    return {
        "type": "opinion",
        "text": sentence.get("text", ""),
        "startIndex": sentence.get("start_index", -1),
        "endIndex": sentence.get("end_index", -1),
        "reason": sentence.get("reason", ""),
    }


def transform_pipeline_result(state: FactCheckState) -> FactcheckResult:
    """
    파이프라인 결과(FactCheckState)를 FactcheckResult로 변환.

    변환 규칙:
    1. 내부 필드 제거: retry_count, whitelist, blacklist
    2. excluded 타입 문장 제외 (claim, opinion만 포함)
    3. claim은 verdict가 있는 경우만 포함 (처리 완료된 것만)
    """
    result_sentences: list[ResultSentence] = []

    for sentence in state["sentences"]:
        sentence_type = sentence.get("type")

        if sentence_type == "claim" and "verdict" in sentence:
            result_sentences.append(transform_claim(sentence))
        elif sentence_type == "opinion":
            result_sentences.append(transform_opinion(sentence))
        # excluded 타입은 무시 (API 응답에 포함하지 않음)

    return {
        "title": state["title"],
        "originalText": state["original_text"],
        "sentences": result_sentences,
    }


def result_to_json_content(result: FactcheckResult) -> str:
    """
    FactcheckResult를 JSON 문자열로 직렬화.

    MCP 프로토콜에서 result.content[].text에 들어갈 문자열 생성.

    Args:
        result: 변환된 팩트체크 결과

    Returns:
        JSON 문자열 (한글 유지: ensure_ascii=False)
    """
    return json.dumps(result, ensure_ascii=False)
