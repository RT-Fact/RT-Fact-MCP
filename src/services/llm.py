"""Gemini API 서비스 래퍼"""

from typing import Literal

from google import genai
from google.genai import types
from pydantic import BaseModel, Field


class ExtractedSentence(BaseModel):
    """추출된 문장 스키마 (LLM 응답용 - 인덱스 없음)"""

    type: Literal["claim", "opinion", "excluded"]
    text: str
    reason: str | None = Field(default=None, description="opinion 또는 excluded인 경우 분류 이유")


class ExtractionResult(BaseModel):
    """문장 추출 결과"""

    title: str = Field(description="텍스트의 핵심 주제를 요약한 제목 (15자 이내)")
    sentences: list[ExtractedSentence]


EXTRACTION_PROMPT = """
You are a fact-checking assistant that extracts and classifies sentences from text.

## Your Task
1. Extract ALL sentences from the given text
2. Classify each sentence into one of three categories
3. Generate a concise title (max 15 characters) that summarizes the main topic

## Classification Criteria

### claim (Fact-checkable)
Sentences containing objective, verifiable information:
- Statistics, numbers, dates, measurements
- Named entities (people, organizations, places)
- Historical events or scientific facts
- Statements that can be verified with external sources
Examples: "The capital of Korea is Seoul.", "Bitcoin was launched in 2009."

### opinion (Subjective)
Sentences expressing personal views, judgments, or preferences:
- Words like "should", "must", "need to" (normative statements)
- Evaluative adjectives: "best", "worst", "beautiful", "terrible"
- Predictions without factual basis
- Personal feelings or beliefs
Examples: "Seoul is a beautiful city.", "This policy will fail."

### excluded (Not fact-checkable)
Sentences that cannot or should not be fact-checked:
- Greetings, farewells
- Questions
- Sentences with only pronouns (no clear referent)
- Incomplete sentences or fragments
- Commands or requests
Examples: "Hello!", "What do you think?", "It is good." (unclear referent)

## Output Requirements
- text: MUST be the EXACT substring from the original text
  (preserve all characters including punctuation)
- reason: Required for opinion and excluded types (explain WHY in Korean, 1 sentence)
- sentences: MUST be returned in the same order they appear in the original text

## Text to Analyze
{text}
"""


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

    async def extract_sentences(self, text: str) -> dict:
        """
        텍스트에서 문장 추출 및 분류

        Args:
            text: 원본 텍스트

        Returns:
            {"title": str, "sentences": list[dict]}
            각 sentence는 type, text, startIndex, endIndex, reason?(opinion/excluded) 포함
        """
        prompt = EXTRACTION_PROMPT.format(text=text)

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractionResult,
                temperature=0.1,  # 일관된 분류를 위해 낮은 temperature
            ),
        )

        result = ExtractionResult.model_validate_json(response.text)

        # 후처리: 원본 텍스트에서 인덱스 계산
        sentences_with_indices = []
        search_start = 0  # 순서대로 검색하여 중복 문장 처리

        for s in result.sentences:
            sentence_dict = s.model_dump(exclude_none=True)

            # 원본 텍스트에서 문장 위치 찾기
            idx = text.find(s.text, search_start)
            if idx != -1:
                sentence_dict["startIndex"] = idx
                sentence_dict["endIndex"] = idx + len(s.text)
                search_start = idx + len(s.text)  # 다음 검색 시작점
            else:
                # 찾지 못한 경우 -1로 표시
                sentence_dict["startIndex"] = -1
                sentence_dict["endIndex"] = -1

            sentences_with_indices.append(sentence_dict)

        return {"title": result.title, "sentences": sentences_with_indices}

    async def verify_claim(self, claim: str, sources: list[dict]) -> dict:
        """
        Claim 검증

        Args:
            claim: 검증할 주장
            sources: 검색된 소스 리스트

        Returns:
            검증 결과 (verdict: TRUE/FALSE, suggestion?)
        """
        # TODO: Gemini API 호출
        pass
