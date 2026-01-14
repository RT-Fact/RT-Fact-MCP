"""JSON-RPC 2.0 표준 에러 코드"""

from enum import IntEnum


class JsonRpcErrorCode(IntEnum):
    """JSON-RPC 2.0 표준 에러 코드"""

    PARSE_ERROR = -32700  # 잘못된 JSON
    INVALID_REQUEST = -32600  # 유효하지 않은 JSON-RPC 요청
    METHOD_NOT_FOUND = -32601  # 메서드 없음
    INVALID_PARAMS = -32602  # 잘못된 파라미터
    INTERNAL_ERROR = -32603  # 내부 에러
