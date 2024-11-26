import os
from typing import Any

import jwt
from dotenv import load_dotenv
from rest_framework import authentication, exceptions, permissions
from rest_framework.request import Request

load_dotenv()


class IsAuthenticatedById(permissions.BasePermission):
    def has_permission(self, request: Request, view: Any) -> bool:
        return request.user is not None and isinstance(request.user, int)


class JWTAuthenticationCustom(authentication.BaseAuthentication):
    def authenticate(self, request: Request) -> tuple[Any, None] | None:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        try:
            payload = jwt.decode(
                auth_header,
                os.getenv("JWT_SECRET"),
                algorithms=[os.getenv("JWT_ALGORITHM")],
                options={"verify_sub": False},
            )
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            raise exceptions.AuthenticationFailed(str(e))

        user_id = payload.get("sub")
        if not user_id:
            raise exceptions.AuthenticationFailed("Token payload is invalid")

        return user_id, None
