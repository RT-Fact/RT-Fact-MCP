"""Tavily Search API 서비스 래퍼"""

import asyncio

from tavily import AsyncTavilyClient

from graph.state import Source

# Snippet 최대 길이 (검색 결과 미리보기용)
SNIPPET_MAX_LENGTH = 200


class TavilyService:
    """Tavily Search API 래퍼 클래스"""

    def __init__(self, api_key: str):
        """
        Args:
            api_key: Tavily API 키
        """
        self.client = AsyncTavilyClient(api_key=api_key)
        # 동시 요청 제한을 위한 세마포어 (최대 3개)
        self.semaphore = asyncio.Semaphore(3)

    async def search(
        self,
        query: str,
        include_domains: list[str] | None = None,  # whitelist
        exclude_domains: list[str] | None = None,  # blacklist
        max_results: int = 3,
    ) -> list[Source]:
        """
        웹 검색 수행

        Args:
            query: 검색 쿼리
            include_domains: 우선 검색 도메인 (whitelist)
            exclude_domains: 제외할 도메인 (blacklist)
            max_results: 최대 결과 개수

        Returns:
            검색 결과 리스트 (title, url, snippet)
        """
        include_domains = include_domains or []
        exclude_domains = exclude_domains or []

        async with self.semaphore:
            response = await self.client.search(
                query=query,
                max_results=max_results,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
            )

        sources: list[Source] = []
        for result in response.get("results", []):
            sources.append(
                Source(
                    title=result.get("title", ""),
                    url=result.get("url", ""),
                    snippet=result.get("content", "")[:SNIPPET_MAX_LENGTH],
                )
            )

        return sources
