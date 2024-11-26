from asgiref.sync import sync_to_async
from django.db import connections


@sync_to_async
def get_email_of_user(user_id: int) -> str | None:
    with connections["user_db"].cursor() as cursor:
        cursor.execute("SELECT email FROM users WHERE id = %s", [user_id])
        result = cursor.fetchone()
        return result[0] or None
