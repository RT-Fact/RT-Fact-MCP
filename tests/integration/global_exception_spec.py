import json

import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from config import get_settings
from main import app, global_exception_handler


@pytest.fixture
def client():
    return TestClient(app)


def test_global_exception_handler_returns_json_rpc_error(client: TestClient):
    """전역 예외 처리기가 JSON-RPC 규격의 에러를 반환하는지 테스트"""
    # 유효하지 않은 JSON 전송 -> JSONDecodeError
    response = client.post("/mcp", content="{invalid-json}")
    assert response.status_code == 200  # JSON-RPC는 에러도 200 OK로 줍니다 (보통)
    data = response.json()
    assert data["error"]["code"] == -32700  # Parse Error


@pytest.mark.asyncio
async def test_handler_traceback_logic() -> None:
    """핸들러 함수 단위 테스트: 환경변수에 따른 Traceback 포함 여부"""

    # 1. Dev 환경 설정
    settings = get_settings()
    settings.environment = "dev"

    # 가짜 요청 Scope 생성
    scope = {
        "type": "http",
        "headers": [],
        "router": None,
        "endpoint": None,
        "path_params": {},
        "query_string": b"",
        "server": ("testserver", 80),
        "client": ("testclient", 50000),
        "scheme": "http",
        "root_path": "",
        "app": app,
    }
    request = Request(scope)

    # 예외 발생 및 핸들러 호출
    try:
        _ = 1 / 0
    except ZeroDivisionError as exc:
        response = await global_exception_handler(request, exc)
        body = json.loads(bytes(response.body))

        # 검증: traceback이 있어야 함
        assert "traceback" in body["error"]["data"]
        assert "ZeroDivisionError" in body["error"]["data"]["traceback"]


@pytest.mark.asyncio
async def test_handler_no_traceback_in_prod(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prod 환경에서는 Traceback이 없어야 함"""

    # 1. Prod 환경 설정
    settings = get_settings()
    monkeypatch.setattr(settings, "environment", "prod")

    scope = {
        "type": "http",
        "headers": [],
        "router": None,
        "endpoint": None,
        "path_params": {},
        "query_string": b"",
        "server": ("testserver", 80),
        "client": ("testclient", 50000),
        "scheme": "http",
        "root_path": "",
        "app": app,
    }
    request = Request(scope)

    try:
        raise ValueError("Critical Secret Error")
    except ValueError as exc:
        response = await global_exception_handler(request, exc)
        body = json.loads(bytes(response.body))

        # 검증: traceback이 없어야 함
        assert "traceback" not in body["error"]["data"]
        assert body["error"]["data"]["detail"] == "Critical Secret Error"
