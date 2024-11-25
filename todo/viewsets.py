from rest_framework.pagination import PageNumberPagination
from rest_framework import (viewsets, status, exceptions, permissions,
                            response, authentication, filters as drf_filters)

class StandardPaginationViewSet(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"


def confirm_invitation(request, task_id, token):
    try:
        task = Task.objects.get(id=task_id)
        user = request.user

        if user.id not in task.user_id:
            task.user_id.append(user.id)
            task.save()
            return redirect('task_detail', task_id=task.id)

    except Task.DoesNotExist:
        return render(request, 'error_page.html', {'error': 'Task not found'})


def send_invitation_email(task, user_email):
    token = uuid4()
    confirmation_url = reverse('confirm_invitation',
                               kwargs={'task_id': task.id, 'token': token})

    send_mail(
        subject=f"Invitation to Task: {task.title}",
        message=f"You've been invited to join the task '{task.title}'. Please click the link below to accept the invitation: {confirmation_url}",
        from_email="no-reply@yourdomain.com",
        recipient_list=[user_email]
    )



class IsAuthenticatedById(permissions.BasePermission):
    def has_permission(self, request, view):
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