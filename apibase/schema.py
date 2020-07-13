import graphene.relay
# https://docs.graphene-python.org/projects/django/en/latest/queries/
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import QuerySet
from . import serializers, filters, utils


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



class NodeSet(DjangoFilterConnectionField):
    # https://github.com/graphql-python/graphene-django/issues/320#issuecomment-404802724

    @property
    def type(self):

        class NodeSetConnection(graphene.Connection):
            total_count = graphene.Int()
            records = graphene.Int()

            class Meta:
                node = self._type
                name = '{}NodeSetConnection'.format(self._type._meta.name)

            def resolve_total_count(self, info, **kwargs):
                return self.length

            def resolve_records(self, info, **kwargs):
                if isinstance(self.iterable, QuerySet):
                    # TODO: each models may have it own countable criteria
                    return self.iterable.model.objects.count()

                return self.length

        return NodeSetConnection

    @classmethod
    def resolve_connection(cls, connection, args, iterable, *nargs, **kwargs):
        # connectioon: NodeSetConnection
        # args: GraphQL Query
        # iterable: QuerySet

        connection = super().resolve_connection(connection, args, iterable, *nargs, **kwargs)

        start_offset = utils.resolve_start_offset(0, args.get('after'))
        connection.page_info.has_previous_page = (start_offset > 0)

        return connection

    obvious_filters = [
        filters.IntFilter,
    ]

    @property
    def filtering_args(self):
        return utils.get_filtering_args_from_filterset(
            self.filterset_class, self.node_type, 
            obvious_filters=self.obvious_filters)
