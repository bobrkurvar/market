import logging

from fastapi import Response
from starlette.requests import HTTPConnection

from core import conf

log = logging.getLogger(__name__)


class AuthCookies:
    def __init__(self):
        self.refresh_token_key = "refresh_token"
        self.access_token_key = "access_token"
        self.cookie_secret = not conf.is_test

    def get_refresh_token(self, request: HTTPConnection):
        return request.cookies.get(self.refresh_token_key)

    def get_access_token(self, request: HTTPConnection):
        return request.cookies.get(self.access_token_key)

    @staticmethod
    def clear_tokens(response: Response):
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")

    def set_refresh_token(self, response: Response, value: str):
        ttl = 86400 * 7
        response.set_cookie(
            self.refresh_token_key,
            value,
            httponly=True,
            max_age=ttl,
            samesite="strict",
            secure=self.cookie_secret,
            path="/",
        )

    def set_access_token(self, response: Response, value: str):
        ttl = 900
        response.set_cookie(
            self.access_token_key,
            value,
            httponly=True,
            max_age=ttl,
            samesite="strict",
            secure=self.cookie_secret,
            path="/",
        )

    def set_tokens(self, access_token: str, refresh_token: str, response: Response):
        self.set_access_token(value=access_token, response=response)
        self.set_refresh_token(value=refresh_token, response=response)
