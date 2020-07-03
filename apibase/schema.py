import graphene.relay
# https://docs.graphene-python.org/projects/django/en/latest/queries/
from . import serializers
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.utils import maybe_queryset
from django.db.models.query import QuerySet

from graphene.relay.connection import PageInfo
# from graphql_relay import connection_from_list
from graphql_relay.connection.arrayconnection import connection_from_list_slice, get_offset_with_default
from functools import partial
from collections.abc import Iterable


class NodeMixin(object):
    # self: Model Class

    pk = graphene.Int()
    endpoint = graphene.String()

    def resolve_pk(self, info):
        return self.pk

    def resolve_endpoint(self, info):
        path = serializers.drf_endpoint(self)
        if hasattr(info.context, 'build_absolute_uri'):
            return info.context.build_absolute_uri(path)
        return path

    @classmethod
    def get_node(cls, info, id):
        queryset = cls.get_queryset(cls._meta.model.objects, info)
        try:
            return queryset.get(pk=id)
        except cls._meta.model.DoesNotExist:
            return None


def connection_adapter(cls, edges, pageInfo):
    """Adapter for creating Connection instances"""
    return cls(edges=edges, page_info=pageInfo)

def page_info_adapter(startCursor, endCursor, hasPreviousPage, hasNextPage):
    """Adapter for creating PageInfo instances"""
    return PageInfo(
        start_cursor=startCursor,
        end_cursor=endCursor,
        has_previous_page=hasPreviousPage,
        has_next_page=hasNextPage,
    )

def resolve_start_offset(slice_start, after):
    after_offset = get_offset_with_default(after, -1)
    return  max(slice_start - 1, after_offset, -1) + 1

class NodeSet(DjangoFilterConnectionField):
    # https://github.com/graphql-python/graphene-django/issues/320#issuecomment-404802724

    @property
    def type(self):

        class NodeSetConnection(graphene.Connection):
            total_count = graphene.Int()

            class Meta:
                node = self._type
                name = '{}NodeSetConnection'.format(self._type._meta.name)

            def resolve_total_count(self, info, **kwargs):
                # return self.iterable.count()
                return self.length

        return NodeSetConnection


    @classmethod
    def resolve_connection(cls, connection, args, iterable):
        # connectioon: NodeSetConnection
        # args: GraphQL Query
        # iterable: QuerySet

        connection = super().resolve_connection(connection, args, iterable)

        start_offset = resolve_start_offset(0, args.get('after'))
        connection.page_info.has_previous_page = (start_offset > 0)

        return connection
