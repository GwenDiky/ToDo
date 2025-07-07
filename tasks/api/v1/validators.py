import httpx
from django.conf import settings
from django.core.exceptions import ValidationError

API_URL = settings.API_URL


def validate_user_exists(user_id: str) -> None:
    with httpx.Client() as client:
        response = client.get(f"{API_URL}/{user_id}")
        if response.status_code != 200:
            raise ValidationError("User with such id doesn't exist.")
        return response.json()


def validate_if_superuser(user_id: str) -> bool:
    with httpx.Client() as client:
        response = client.get(f"{API_URL}/{user_id}/is-superuser")
        if response.status_code == 200:
            return response.json()
        raise ValidationError("Requested user isn't a superuser")
