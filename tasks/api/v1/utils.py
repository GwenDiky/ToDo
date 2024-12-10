import httpx
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.exceptions import ValidationError
from urllib.parse import urlparse

API_URL = settings.API_URL


@sync_to_async
def get_email_of_user(user_id: int) -> str | None:
    with httpx.Client() as client:
        response = client.get(f"{API_URL}/{user_id}/email")
        if response.status_code == 200:
            return response.json()
        raise ValidationError("User with such id doesn't exist")


def extract_file_info(attachment_url):
    path = urlparse(attachment_url).path
    file_name = path.split("/")[-1]
    file_type = file_name.split(".")[-1] if "." in file_name else None
    return file_name, file_type
