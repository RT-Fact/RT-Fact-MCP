"""Gemini API 서비스 래퍼"""

from typing import Literal

from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from services.prompts import EXTRACTION_PROMPT, VERIFICATION_PROMPT


class ExtractedSentence(BaseModel):
    """추출된 문장 스키마 (LLM 응답용 - 인덱스 없음)"""

    type: Literal["claim", "opinion", "excluded"]
    text: str
    reason: str | None = Field(default=None, description="opinion 또는 excluded인 경우 분류 이유")


class ExtractionResult(BaseModel):
    """문장 추출 결과"""

    title: str = Field(description="텍스트의 핵심 주제를 요약한 제목 (15자 이내)")
    sentences: list[ExtractedSentence]


class VerificationResult(BaseModel):
    """검증 결과 스키마"""

    verdict: Literal["TRUE", "FALSE"] = Field(description="사실 여부 판정")
    suggestion: str | None = Field(default=None, description="FALSE 판정 시 수정 제안")


class GeminiService:
    """Gemini API 래퍼 클래스"""

    def __init__(self, api_key: str):
        """
        Args:
            api_key: Gemini API 키
        """
        self.client = genai.Client(api_key=api_key)
        # TODO: 모델명 관리(환경 변수 or 설정 파일)
        self.model = "gemini-2.5-flash-lite"

    @retry(
        retry=retry_if_exception_type((errors.ServerError, errors.ClientError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def _generate_content(self, contents: str, response_schema: type[BaseModel]):
        """재시도 로직이 적용된 내부 generate_content 메서드"""
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=0.1,
        )
        return await self.client.aio.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )

    async def extract_sentences(self, text: str) -> dict:
        """
        텍스트에서 문장 추출 및 분류

        Args:
            text: 원본 텍스트

        Returns:
            {"title": str, "sentences": list[dict]}
            각 sentence는 type, text, start_index, end_index, reason?(opinion/excluded) 포함
        """
        prompt = EXTRACTION_PROMPT.format(text=text)

        response = await self._generate_content(prompt, ExtractionResult)

        result = ExtractionResult.model_validate_json(response.text)

        # 후처리: 원본 텍스트에서 인덱스 계산
        sentences_with_indices = []
        search_start = 0  # 순서대로 검색하여 중복 문장 처리

        for s in result.sentences:
            sentence_dict = s.model_dump(exclude_none=True)

            # 원본 텍스트에서 문장 위치 찾기
            idx = text.find(s.text, search_start)
            if idx != -1:
                sentence_dict["start_index"] = idx
                sentence_dict["end_index"] = idx + len(s.text)
                search_start = idx + len(s.text)  # 다음 검색 시작점
            else:
                # 찾지 못한 경우 -1로 표시
                sentence_dict["start_index"] = -1
                sentence_dict["end_index"] = -1

            sentences_with_indices.append(sentence_dict)

        return {"title": result.title, "sentences": sentences_with_indices}

    async def verify_claim(self, claim: str, sources: list[dict]) -> dict:
        """
        Claim 검증

        Args:
            claim: 검증할 주장
            sources: 검색된 소스 리스트 [{"title": str, "url": str, "snippet": str}, ...]

        Returns:
            {"verdict": "TRUE" | "FALSE", "suggestion": str | None}
        """

        # sources를 문자열로 포맷팅
        sources_text = "\n\n".join(
            f"### {s.get('title', 'Untitled')}\n"
            f"URL: {s.get('url', 'N/A')}\n"
            f"Content: {s.get('snippet', '')}"
            for s in sources
        )

        prompt = VERIFICATION_PROMPT.format(claim=claim, sources=sources_text)

        response = await self._generate_content(prompt, VerificationResult)

        result = VerificationResult.model_validate_json(response.text)
        return result.model_dump(exclude_none=True)
