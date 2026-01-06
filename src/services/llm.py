"""Gemini API 서비스 래퍼"""
from google import genai
import os
from typing import Any


class GeminiService:
    """Gemini API 래퍼 클래스"""
    
    def __init__(self, api_key: str):
        """
        Args:
            api_key: Gemini API 키
        """
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash-001"
    
    async def extract_sentences(self, text: str) -> list[dict]:
        """
        텍스트에서 문장 추출 및 분류
        
        Args:
            text: 원본 텍스트
            
        Returns:
            문장 리스트 (type, text, startIndex, endIndex, reason?)
        """
        # TODO: Gemini API 호출
        # - JSON mode 사용
        # - 타임아웃 30초
        # - 재시도 최대 3회
        pass
    
    async def verify_claim(
        self, 
        claim: str, 
        sources: list[dict]
    ) -> dict:
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
