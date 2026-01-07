# RT-Fact MCP Server

검색 기능과 AI 모델을 사용해 팩트 검증 기능을 제공하는 MCP 서버

## 요구사항

- Python 3.13+
- [Poetry](https://python-poetry.org/)

## 설치

```bash
# 의존성 설치
poetry install

# 환경변수 설정
cp .env.example .env
# .env 파일에 GEMINI_API_KEY, TAVILY_API_KEY 설정
```

## 테스트 실행

```bash
# 전체 테스트
poetry run pytest

# 특정 테스트 파일
poetry run pytest tests/graph/nodes_spec.py -v

# E2E 테스트 (실제 API 호출, API 키 필요)
PYTHONPATH=src poetry run python scripts/test_extraction_e2e.py
```

## 개발 서버 실행

```bash
poetry run uvicorn src.main:app --reload
```
