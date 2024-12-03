from django.http import JsonResponse


class ApiException(Exception):
    status_code = 400
    default_detail: str = "An unexpected error occurred."
    default_headers: dict = {}

    def __init__(self, detail=None, headers=None, status_code=None):
        self.detail = detail or self.default_detail
        self.headers = headers or self.default_headers
        self.status_code = status_code or self.status_code

    def as_response(self):
        response = JsonResponse(
            {"detail": self.detail}, status=self.status_code
        )
        for key, value in self.headers.items():
            response[key] = value
        return response


class EmailSendingFailedException(ApiException):
    detail = "Failed to send email due to an internal error."


class EmailVerificationFailedException(ApiException):
    detail = "Email verification failed."


class PermissionDeniedException(ApiException):
    detail = "Permission denied."
    status_code = 403


class ValidationFailedException(ApiException):
    detail = "Validation failed."
    status_code = 400
