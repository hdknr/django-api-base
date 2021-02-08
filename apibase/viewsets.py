from rest_framework import viewsets, decorators, status
from rest_framework.response import Response
from django.contrib.auth.models import Permission
from . import paginations, permissions


class BaseModelViewSet(viewsets.ModelViewSet):
    pagination_class = paginations.Pagination

    @decorators.action(methods=["post"], detail=False)
    def batch_create(self, request, *args, **kwargs):
        if request.method == 'GET':
            return self.list(request)
        return self.create(request, many=True)

    @decorators.action(methods=['patch', 'get'], detail=False)
    def batch_update(self, request):
        if request.method == 'GET':
            return self.list(request)
        return self.update(request, pk=None, many=True, partial=True)

    @classmethod
    def permissions(cls):
        return [
            Permission.objects.filter(
                **dict(
                    zip(("content_type__app_label", "codename"), p.PERM_CODE.split("."))
                )
            ).first()
            for p in cls.permission_classes
            if issubclass(p, permissions.Permission) and p.PERM_CODE
        ]

    def update(self, request, *args, **kwargs):
        """(override)"""
        many = kwargs.pop("many", False)
        if many:
            return self.update_batch(request, *args, **kwargs)
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """(override)"""
        many = kwargs.pop("many", False)
        if many:
            return self.create_batch(request, *args, **kwargs)
        return super().create(request, *args, **kwargs)
        
    def update_batch(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(
            self.filter_queryset(self.get_queryset()),
            data=request.data,
            many=True,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def create_batch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)