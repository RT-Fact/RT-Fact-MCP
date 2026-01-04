"""Factcheck 도구 스키마"""

from pydantic import BaseModel


class FactcheckArguments(BaseModel):
    """factcheck 도구 인자"""

    text: str
    whitelist: list[str] = []
    blacklist: list[str] = []
