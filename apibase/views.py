import mimetypes
import posixpath
from pathlib import Path

import rest_framework
from django.http import FileResponse, Http404, HttpResponse, HttpResponseNotModified
from django.utils._os import safe_join
from django.utils.translation import gettext as _
from django.views import static
from graphene_django import settings, views
from graphql.utils import schema_printer
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from django.utils.http import http_date


def _decorate(view):
    view = permission_classes((IsAuthenticated,))(view)
    view = authentication_classes(api_settings.DEFAULT_AUTHENTICATION_CLASSES)(view)
    return api_view(["GET", "POST"])(view)


class DRFAuthenticatedGraphQLView(views.GraphQLView):
    def parse_body(self, request):
        if isinstance(request, rest_framework.request.Request):
            return request.data
        return super().parse_body(request)

    @classmethod
    def as_view(cls, *args, **kwargs):
        return _decorate(super().as_view(*args, **kwargs))


@_decorate
def sdl(request):
    """GraphQL Schema Definition Language (SDL). """
    schema_str = schema_printer.print_schema(settings.graphene_settings.SCHEMA)
    return HttpResponse(schema_str, content_type="text/plain")


def serve(request, path, document_root=None, as_attachment=False, filename=None):
    path = posixpath.normpath(path).lstrip("/")
    fullpath = Path(safe_join(document_root, path))
    if fullpath.is_dir():
        raise Http404(_("Directory indexes are not allowed here."))
    # Respect the If-Modified-Since header.
    statobj = fullpath.stat()
    if not static.was_modified_since(
        request.META.get("HTTP_IF_MODIFIED_SINCE"), statobj.st_mtime, statobj.st_size
    ):
        return HttpResponseNotModified()
    content_type, encoding = mimetypes.guess_type(str(fullpath))
    content_type = content_type or "application/octet-stream"
    response = FileResponse(
        fullpath.open("rb"),
        content_type=content_type,
        filename=filename,
        as_attachment=as_attachment,
    )
    response["Last-Modified"] = http_date(statobj.st_mtime)
    if encoding:
        response["Content-Encoding"] = encoding
    return response
