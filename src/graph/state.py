"""LangGraph 파이프라인 상태 정의 모듈"""

from typing import List, Optional, TypedDict


class Sentence(TypedDict, total=False):
    """검증 대상 문장 정보"""

    claim: str  # 검증할 핵심 주장
    evidence: Optional[str]  # 검색된 증거 (Optional)
    result: Optional[str]  # 판정 결과 (True/False)
    reasoning: Optional[str]  # 판정 이유


class FactCheckState(TypedDict):
    """
    팩트체크 파이프라인의 상태를 관리하는 스키마입니다.
    START -> Extraction -> Search -> Verification -> END 흐름에서 유지됩니다.
    """

    original_text: str  # 검증할 원본 텍스트 본문
    whitelist: List[str]  # (Optional) 우선 검토할 신뢰 도메인 목록
    blacklist: List[str]  # (Optional) 검색 결과에서 제외할 도메인 목록
    title: str  # Extraction 단계에서 추출한 핵심 주제/제목
    sentences: List[Sentence]  # 각 단계별로 정보가 누적될 문장 리스트
