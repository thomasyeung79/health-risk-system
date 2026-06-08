"""Authentication API client."""

from typing import Any, Optional

from api_client.client import ApiClient


class AuthClient:
    """Client for auth endpoints: register, login, logout, refresh, me."""

    def __init__(self, client: ApiClient):
        self._client = client

    def register(
        self,
        username: str,
        password: str,
        display_name: Optional[str] = None,
        preferred_language: str = "English",
    ) -> dict[str, Any]:
        """Register a new user. Returns user profile on success."""
        return self._client.post("/api/v1/auth/register", json={
            "username": username,
            "password": password,
            "display_name": display_name or username,
            "preferred_language": preferred_language,
        })

    def login(self, username: str, password: str) -> dict[str, Any]:
        """Authenticate and return token pair + user profile."""
        result = self._client.post("/api/v1/auth/login", json={
            "username": username,
            "password": password,
        })
        self._client.set_tokens(result["access_token"], result["refresh_token"])
        return result

    def logout(self) -> dict[str, Any]:
        """Revoke the current refresh token."""
        if self._client.refresh_token:
            try:
                return self._client.post("/api/v1/auth/logout", json={
                    "refresh_token": self._client.refresh_token,
                })
            finally:
                self._client.clear_tokens()
        self._client.clear_tokens()
        return {"message": "Logged out"}

    def refresh(self) -> dict[str, Any]:
        """Exchange current refresh token for a new token pair."""
        if not self._client.refresh_token:
            raise ValueError("No refresh token available")
        result = self._client.post("/api/v1/auth/refresh", json={
            "refresh_token": self._client.refresh_token,
        })
        self._client.set_tokens(result["access_token"], result["refresh_token"])
        return result

    def me(self) -> dict[str, Any]:
        """Get the currently authenticated user's profile."""
        return self._client.get("/api/v1/auth/me")
