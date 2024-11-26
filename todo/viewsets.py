import os

import jwt
from dotenv import load_dotenv
from rest_framework import authentication, exceptions, permissions
from rest_framework.pagination import PageNumberPagination

load_dotenv()


class StandardPaginationViewSet(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
