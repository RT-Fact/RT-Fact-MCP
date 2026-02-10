"""Factcheck 도구 스키마 (Input/Output)"""

from typing import Literal, TypedDict

from pydantic import BaseModel

from factcheck.state import Source

# ============================================================
# Input (요청)
# ============================================================


class FactcheckArguments(BaseModel):
    """factcheck 도구 인자"""

    text: str
    whitelist: list[str] = []
    blacklist: list[str] = []


# ============================================================
# Output (결과)
# ============================================================


class ClaimSentence(TypedDict):
    """검증 대상 문장 (claim)"""

    type: Literal["claim"]
    text: str
    startIndex: int
    endIndex: int
    verdict: Literal["TRUE", "FALSE"]
    sources: list[Source]
    suggestion: str | None


class OpinionSentence(TypedDict):
    """의견 문장 (opinion)"""

    type: Literal["opinion"]
    text: str
    startIndex: int
    endIndex: int
    reason: str


ResultSentence = ClaimSentence | OpinionSentence


class FactcheckResult(TypedDict):
    """팩트체크 결과 페이로드

    tools/call 응답의 content[].text에 JSON으로 직렬화되어 담기는 구조.
    NestJS 백엔드와의 계약(Contract).
    """

    title: str
    originalText: str
    sentences: list[ResultSentence]
