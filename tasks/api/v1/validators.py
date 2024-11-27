from django.core.exceptions import ValidationError
from django.db import connections


def validate_user_exists(user_id: str) -> None:
    with connections["user_db"].cursor() as cursor:
        cursor.execute("SELECT id FROM users WHERE id = %s", [user_id])
        if not cursor.fetchone():
            raise ValidationError(f"User with id {user_id} doesn't exist.")


def validate_if_superuser(user_id: str) -> bool:
    with connections["user_db"].cursor() as cursor:
        cursor.execute(
            "SELECT is_superuser FROM users WHERE id = %s", [user_id]
        )
        result = cursor.fetchone()
        if result is None:
            raise ValidationError(f"User with id {user_id} doesn't exist.")
        return result[0]
