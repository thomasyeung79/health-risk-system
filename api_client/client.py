"""Base API client with JWT handling, auto-refresh, and unified error handling."""

from __future__ import annotations

import os
from typing import Any, Optional

import requests


class ApiError(Exception):
    """Raised when the API returns a non-success status code."""

    def __init__(self, status_code: int, detail: str = ""):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API {status_code}: {detail}")


class ApiClient:
    """Shared HTTP client for calling the FastAPI backend.

    Handles JWT access tokens, automatic token refresh on 401,
    and raises ApiError for non-success responses.
    """

    def __init__(self, base_url: str = ""):
        if not base_url:
            base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None

    # ── Token management ────────────────────────────────

    @property
    def access_token(self) -> Optional[str]:
        return self._access_token

    @property
    def refresh_token(self) -> Optional[str]:
        return self._refresh_token

    def set_tokens(self, access_token: str, refresh_token: str) -> None:
        """Store both tokens after login or refresh."""
        self._access_token = access_token
        self._refresh_token = refresh_token

    def clear_tokens(self) -> None:
        """Clear tokens on logout or session expiry."""
        self._access_token = None
        self._refresh_token = None

    @property
    def is_authenticated(self) -> bool:
        return self._access_token is not None

    def _build_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers

    # ── Core request method ─────────────────────────────

    def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        """Send an HTTP request with automatic JWT refresh.

        Returns the parsed JSON response body on success.
        Raises ApiError on non-2xx status codes.
        """
        url = f"{self.base_url}{path}"
        headers = self._build_headers()

        # Merge headers with any per-request headers
        req_headers = kwargs.pop("headers", {})
        headers.update(req_headers)

        resp = self._session.request(method, url, headers=headers, **kwargs)

        # Auto-refresh on 401 if refresh token is available
        if resp.status_code == 401 and self._refresh_token:
            refreshed = self._try_refresh()
            if refreshed:
                headers = self._build_headers()
                headers.update(req_headers)
                resp = self._session.request(method, url, headers=headers, **kwargs)

        if not 200 <= resp.status_code < 300:
            detail = ""
            try:
                body = resp.json()
                detail = body.get("detail", str(body))
            except Exception:
                detail = resp.text[:200]
            raise ApiError(resp.status_code, detail)

        try:
            return resp.json()
        except Exception:
            return resp.text

    # ── HTTP verb shortcuts ─────────────────────────────

    def get(self, path: str, **kwargs: Any) -> Any:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Any:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Any:
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Any:
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Any:
        return self.request("DELETE", path, **kwargs)

    # ── Internal helpers ────────────────────────────────

    def _try_refresh(self) -> bool:
        """Attempt to refresh the access token.

        Returns True if successful, False otherwise.
        """
        try:
            resp = self._session.post(
                f"{self.base_url}/api/v1/auth/refresh",
                json={"refresh_token": self._refresh_token},
            )
            if resp.status_code == 200:
                data = resp.json()
                self._access_token = data["access_token"]
                self._refresh_token = data["refresh_token"]
                return True
        except Exception:
            pass

        self.clear_tokens()
        return False
