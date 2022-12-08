from typing import Dict

from httpx import AsyncClient

from auo_project.core.config import settings


class AuthTestClient(AsyncClient):
    _cookies: Dict = None

    async def ensure_authed(self) -> None:
        if not self._cookies:
            req = self.build_request(
                "POST",
                f"{self.base_url}/api/v1/auth/token/login",
                data={
                    "username": settings.FIRST_SUPERUSER_EMAIL,
                    "password": settings.FIRST_SUPERUSER_PASSWORD,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            resp = await self.send(req)
            assert resp.status_code == 200
            self._cookies = resp.cookies

    async def request(self, *args, **kwargs):
        await self.ensure_authed()
        cookies_assigned = kwargs and kwargs["cookies"]
        if cookies_assigned is None and self._cookies.get("access_token_cookie"):
            kwargs["cookies"] = {
                "access_token_cookie": self._cookies.get("access_token_cookie"),
                "csrf_access_token": self._cookies.get("csrf_access_token"),
            }
            kwargs["headers"] = {"X-CSRF-TOKEN": self._cookies.get("csrf_access_token")}
        return await super().request(*args, **kwargs)
