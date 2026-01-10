import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor


def configure_logger() -> None:
    """Structlog 설정 초기화"""

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # 파이썬 표준 로깅 설정 (JSON 포맷터 연결)
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            _drop_color_message_key,
            structlog.processors.JSONRenderer(),
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


def _drop_color_message_key(_: Any, __: Any, event_dict: EventDict) -> EventDict:
    """Uvicorn 등에서 넘어오는 color_message 키 제거 (JSON 로그 오염 방지)"""
    event_dict.pop("color_message", None)
    return event_dict


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """로거 인스턴스 반환"""
    return structlog.get_logger(name)
