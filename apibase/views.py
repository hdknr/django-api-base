from graphene_django import views, settings
from graphql.utils import schema_printer

from django.http import HttpResponse
import rest_framework
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.settings import api_settings


def _decorate(view):
    view = permission_classes((IsAuthenticated,))(view)
    view = authentication_classes(api_settings.DEFAULT_AUTHENTICATION_CLASSES)(view)
    return api_view(['GET', 'POST'])(view)


class DRFAuthenticatedGraphQLView(views.GraphQLView):
    def parse_body(self, request):
        if isinstance(request, rest_framework.request.Request):
            return request.data
        return super().parse_body(request)

    @classmethod
    def as_view(cls, *args, **kwargs):
        return _decorate(super().as_view(*args, **kwargs))


@_decorate
def dsl(request):
    schema_str = schema_printer.print_schema(settings.graphene_settings.SCHEMA)
    return HttpResponse(schema_str, content_type='text/plain')
