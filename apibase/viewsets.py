from rest_framework import (
    viewsets, response, decorators)
from .paginations import Pagination


class BaseModelViewSet(viewsets.ModelViewSet):
    pagination_class = Pagination
