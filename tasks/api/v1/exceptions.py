from django.http import JsonResponse

class EmailSendingFailedException(Exception):
    status_code = 500
    default_detail = "Failed to send email due to an internal error."
    default_headers = {}

    def __init__(self, detail=None, headers=None):
        self.detail = detail or self.default_detail
        self.headers = headers or self.default_headers

    def as_response(self):
        response = JsonResponse({"detail": self.detail}, status=self.status_code)
        for key, value in self.headers.items():
            response[key] = value
        return response


class EmailVerificationFailedException(Exception):
    status_code = 400
    default_detail = "Email verification failed."
    default_headers = {}

    def __init__(self, sender_email=None, detail=None, headers=None):
        self.sender_email = sender_email
        self.detail = detail or self.default_detail
        if sender_email:
            self.detail = f"Failed to verify email: {sender_email}."
        self.headers = headers or self.default_headers

    def as_response(self):
        response = JsonResponse({"detail": self.detail}, status=self.status_code)
        for key, value in self.headers.items():
            response[key] = value
        return response
