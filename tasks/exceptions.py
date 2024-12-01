from django.http import JsonResponse


class ApiException(Exception):
    status_code = 400
    default_detail: str = "An unexpected error occurred."
    default_headers: dict = {}

    def __init__(self, detail=None, headers=None):
        self.detail = detail or self.default_detail
        self.headers = headers or self.default_headers

    def as_response(self):
        response = JsonResponse(
            {"detail": self.detail}, status=self.status_code
        )
        for key, value in self.headers.items():
            response[key] = value
        return response


class EmailSendingFailedException(ApiException):
    default_detail = "Failed to send email due to an internal error."


class EmailVerificationFailedException(ApiException):
    default_detail = "Email verification failed."
