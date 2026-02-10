"""MCP 인증 관련 메시지 템플릿"""

from config import get_settings

SERVICE_UNAVAILABLE_MESSAGE = """## ⚠️ 일시적 오류

인증 서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.
"""


def get_auth_required_message() -> str:
    """
    인증 실패 시 반환할 사용자 친화적 Markdown 메시지를 생성합니다.

    Returns:
        str: API Key 발급 안내가 포함된 Markdown 문자열
    """
    settings = get_settings()
    frontend_url = settings.frontend_url

    return f"""## 🔒 인증이 필요합니다

이 기능을 사용하려면 **API Key** 설정이 필요합니다.
아래 링크에서 키를 발급받아 설정해주세요.

- 🔗 **발급 페이지**: [{frontend_url}/settings]({frontend_url}/settings)
- ⚙️ **설정 방법**: Cursor/Claude 설정의 `env` 또는 `headers`에 추가

```json
{{
  "headers": {{
    "Authorization": "Bearer rtf_your_api_key_here"
  }}
}}
```
"""
