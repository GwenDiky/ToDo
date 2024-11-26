import os

import jwt
from dotenv import load_dotenv
from rest_framework import (exceptions, permissions,
                            authentication)
from rest_framework.pagination import PageNumberPagination

load_dotenv()


class IsAuthenticatedById(permissions.BasePermission):
    def has_permission(self, request):
        return isinstance(request.user, int)


class JWTAuthenticationCustom(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')
        if not token:
            return None

        try:
            decoded_token = jwt.decode(
                token,
                os.getenv("JWT_SECRET"),
                algorithms=[os.getenv("JWT_ALGORITHM")],
                options={"verify_sub": False}
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")

        user_id = decoded_token.get("sub")
        if not user_id:
            raise exceptions.AuthenticationFailed("Token payload is invalid")

        return (user_id, None)
