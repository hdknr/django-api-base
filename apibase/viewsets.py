from rest_framework import viewsets, decorators, status, serializers
from rest_framework.response import Response
from django.contrib.auth.models import Permission
from django.utils.functional import cached_property
from . import paginations, permissions, utils
from pathlib import Path
from django.views import static


class BaseModelViewSet(viewsets.ModelViewSet):
    pagination_class = paginations.Pagination
    fields_query = None

    @decorators.action(methods=["post"], detail=False)
    def batch_create(self, request, *args, **kwargs):
        if request.method == "GET":
            return self.list(request)
        return self.create(request, many=True)

    @decorators.action(methods=["patch", "get"], detail=False)
    def batch_update(self, request):
        if request.method == "GET":
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
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def paginate_queryset(self, queryset):
        """(override)"""
        # dirty coding for CSV rendering
        if self.request.META.get("HTTP_ACCEPT", None) == "text/csv":
            return None
        return super().paginate_queryset(queryset)

    def get_serializer(self, *args, **kwargs):
        """(override)"""
        ser = super().get_serializer(*args, **kwargs)

        if isinstance(ser, serializers.ListSerializer):
            self._fields = ser.child.fields
        else:
            self._fields = ser.fields
        return ser

    @cached_property
    def label_map(self):
        fields = getattr(self, "_fields", {})
        return dict((name, f.label) for name, f in fields.items())

    def get_renderer_context(self):
        """(override)"""
        fields_query = getattr(self, "fields_query", None)

        context = super().get_renderer_context()
        if not fields_query:
            return context

        # dirty  coding header(list) and lable(dict)
        context["header"] = (
            self.request.GET[fields_query].split(",")
            if fields_query in self.request.GET
            else None
        )

        context["labels"] = (
            dict((i, self.label_map.get(i, i)) for i in context["header"])
            if context["header"]
            else self.label_map
        )

        return context

    @decorators.action(
        methods=["get"], detail=True, url_path="(?P<field>[^/.]+)/download"
    )
    def download_filefield(self, request, pk, field):
        """ download FileField file """
        instance = self.get_object()
        field = getattr(instance, field, None)
        name = str(instance)
        ext = Path(field.path).suffix
        filename = f"{field.field.verbose_name}.{name}{ext}"
        disposition = utils.to_content_disposition(filename)
        res = static.serve(
            self.request,
            field.path,
            document_root="/",
        )
        res["Content-Disposition"] = disposition
        return res
