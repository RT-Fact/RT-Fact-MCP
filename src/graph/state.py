from operator import add
from typing import Annotated, Literal, TypedDict


class Source(TypedDict):
    """검색 결과 출처"""

    title: str
    url: str
    snippet: str


class PipelineSentence(TypedDict, total=False):
    """
    파이프라인 내부에서 점진적으로 채워지는 문장 구조.
    total=False로 모든 필드가 선택적 (노드별로 점진적 추가).
    """

    # ===== 공통 (Extraction에서 채움) =====
    type: Literal["claim", "opinion", "excluded"]
    text: str
    start_index: int
    end_index: int
    retry_count: int  # 재검색 횟수 (기본값 0)

    # ===== 검색 필터 (workflow에서 전달) =====
    whitelist: list[str]  # 우선 검색 도메인
    blacklist: list[str]  # 제외할 도메인

    # ===== opinion/excluded용 =====
    reason: str  # 의견/제외 분류 이유

    # ===== claim용 (Search에서 채움) =====
    sources: list[Source]

    # ===== claim용 (Verification에서 채움) =====
    verdict: Literal["TRUE", "FALSE"]
    suggestion: str | None  # FALSE일 때 수정 제안


class FactCheckState(TypedDict):
    """
    팩트체크 파이프라인의 상태를 관리하는 스키마입니다.
    START -> Extraction -> Search -> Verification -> END 흐름에서 유지됩니다.
    """

    original_text: str  # 검증할 원본 텍스트 본문
    whitelist: list[str]  # (Optional) 우선 검토할 신뢰 도메인 목록
    blacklist: list[str]  # (Optional) 검색 결과에서 제외할 도메인 목록
    title: str  # Extraction 단계에서 추출한 핵심 주제/제목
    sentences: Annotated[list[PipelineSentence], add]  # 추출된 문장 리스트 (Reducer 적용)


class ExtractionOutput(TypedDict):
    """Extraction 노드의 부분 반환 타입"""

    title: str
    sentences: list[PipelineSentence]
