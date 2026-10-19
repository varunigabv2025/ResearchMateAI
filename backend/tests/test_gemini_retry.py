"""Tests for bounded retries of transient Gemini API failures."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.llm_service import LLMService


def make_response(status_code: int) -> httpx.Response:
    request = httpx.Request("POST", "https://generativelanguage.googleapis.com/test")
    return httpx.Response(
        status_code=status_code,
        request=request,
        json={"error": {"code": status_code, "status": "TEST"}},
    )


@pytest.fixture
def service() -> LLMService:
    instance = LLMService()
    instance.max_retries = 3
    instance.retry_base_delay = 0
    return instance


@pytest.mark.asyncio
async def test_retries_transient_gemini_500_then_succeeds(service):
    client = MagicMock()
    client.post = AsyncMock(side_effect=[make_response(500), make_response(200)])

    with patch("app.services.llm_service.asyncio.sleep", new_callable=AsyncMock) as sleep:
        response = await service._post_gemini_with_retry(
            client=client,
            url="https://generativelanguage.googleapis.com/test",
            payload={},
            headers={},
            params={},
        )

    assert response.status_code == 200
    assert client.post.await_count == 2
    sleep.assert_awaited_once()


@pytest.mark.asyncio
async def test_retries_exhausted_500_raise_http_error(service):
    client = MagicMock()
    client.post = AsyncMock(
        side_effect=[make_response(500), make_response(500), make_response(500), make_response(500)]
    )

    with patch("app.services.llm_service.asyncio.sleep", new_callable=AsyncMock) as sleep:
        with pytest.raises(httpx.HTTPStatusError):
            await service._post_gemini_with_retry(
                client=client,
                url="https://generativelanguage.googleapis.com/test",
                payload={},
                headers={},
                params={},
            )

    assert client.post.await_count == service.max_retries + 1
    assert sleep.await_count == service.max_retries


@pytest.mark.asyncio
async def test_does_not_retry_non_transient_client_error(service):
    client = MagicMock()
    client.post = AsyncMock(return_value=make_response(400))

    with patch("app.services.llm_service.asyncio.sleep", new_callable=AsyncMock) as sleep:
        with pytest.raises(httpx.HTTPStatusError):
            await service._post_gemini_with_retry(
                client=client,
                url="https://generativelanguage.googleapis.com/test",
                payload={},
                headers={},
                params={},
            )

    assert client.post.await_count == 1
    sleep.assert_not_awaited()
