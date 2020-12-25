from rest_framework import (viewsets, decorators, status)
from rest_framework.response import Response
from django.contrib.auth.models import Permission
from . import paginations, permissions


class BaseModelViewSet(viewsets.ModelViewSet):
    pagination_class = paginations.Pagination

    def get_serializer(self, *args, **kwargs):
        if self.action == 'batch_create' and self.request.POST:
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)

    @decorators.action(methods=['post'], detail=False)
    def batch_create(self, request, *args, **kwargs):
        # only 'many=True' is added to super().create()
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @classmethod
    def permissions(cls):
        return [
            Permission.objects.filter(
                **dict(zip(('content_type__app_label', 'codename'), p.PERM_CODE.split('.'))))
            for p in cls.permission_classes
            if issubclass(p, permissions.Permission) and p.PERM_CODE
        ]
