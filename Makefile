.PHONY: help dev test check format

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## 서버 실행 (Dev Mode)
	PYTHONPATH=src poetry run uvicorn src.main:app --reload

test: ## 테스트 실행
	poetry run pytest

check: ## 코드 품질 검사 (Ruff, Pyright)
	poetry run ruff check .
	poetry run pyright

format: ## 코드 포맷팅
	poetry run ruff check --fix .
	poetry run ruff format .
