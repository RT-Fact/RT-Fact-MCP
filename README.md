# RT-Fact MCP Server

검색 기능과 AI 모델을 사용해 팩트 검증 기능을 제공하는 MCP 서버

## 요구사항

- Python 3.13+
- [Poetry](https://python-poetry.org/)

## 설치

```bash
# 의존성 설치
poetry install

# pre-commit 훅 설치 (최초 1회)
poetry run pre-commit install
poetry run pre-commit install --hook-type commit-msg

# 환경변수 설정
cp .env.example .env
# .env 파일에 GEMINI_API_KEY, TAVILY_API_KEY 설정
```

## 린팅 & 포맷팅

이 프로젝트는 [ruff](https://docs.astral.sh/ruff/)를 사용하며, [pre-commit](https://pre-commit.com/)으로 자동 실행됩니다.

### 자동 실행 (커밋/푸시 시)

| 훅 | 실행 시점 | 동작 |
|----|----------|------|
| `ruff` | 커밋 | 린팅 + 자동 수정 |
| `ruff-format` | 커밋 | 코드 포맷팅 |
| `commitizen` | 커밋 | 커밋 메시지 검증 |
| `ruff check .` | 푸시 | 전체 파일 린트 체크 |
| `ruff format --check .` | 푸시 | 전체 파일 포맷 체크 |

### 수동 실행

```bash
# 린팅 체크
poetry run ruff check .

# 린팅 + 자동 수정
poetry run ruff check --fix .

# 포맷팅
poetry run ruff format .
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
PYTHONPATH=src poetry run uvicorn main:app --reload
```
