import graphene.relay
# https://docs.graphene-python.org/projects/django/en/latest/queries/
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.rest_framework.mutation import SerializerMutation
from graphql_relay import from_global_id
from graphene.types import resolver, generic
from django.db.models import QuerySet
import decimal
from django.core.serializers.json import DjangoJSONEncoder
from . import serializers, filters, utils
import json


class JSONEncode(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, (decimal.Decimal)):
            return float(o)

        return super().default(o)


def default_resolver(attname, default_value, root, info, **args):
    '''root: model instance, info:graphql.execution.base.ResolveInfo'''
    res = resolver.default_resolver(attname, default_value, root, info, **args)
    if hasattr(info.parent_type.graphene_type, 'patch_result'):
        return info.parent_type.graphene_type.patch_result(res, attname, default_value, root, info, **args)
    return res


class NodeMixin(object):
    # self: Model Class

    pk = graphene.Int()
    endpoint = graphene.String()
    urn = graphene.String()
    display = graphene.String()

    def resolve_pk(self, info):
        return self.pk

    def resolve_endpoint(self, info):
        path = serializers.drf_endpoint(self)
        if hasattr(info.context, 'build_absolute_uri'):
            return info.context.build_absolute_uri(path)
        return path

    def resolve_urn(self, info):
        return serializers.to_urn(self)

    def resolve_display(self, info):
        return str(self)

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
            summary = generic.GenericScalar()

            class Meta:
                node = self._type
                name = '{}NodeSetConnection'.format(self._type._meta.name)

            def resolve_total_count(self, info, **kwargs):
                return self.length

            def resolve_summary(self, info, **kwargs):
                if isinstance(self.iterable, QuerySet) and hasattr(self.iterable, 'summary'):
                    data = json.dumps(self.iterable.summary(), cls=JSONEncode)
                    return json.loads(data)
                return None

            def resolve_records(self, info, **kwargs):
                if isinstance(self.iterable, QuerySet):
                    # TODO: each models may have it own countable criteria
                    return self.iterable.order_by('id').distinct().count()

                return self.length

        return NodeSetConnection

    @classmethod
    def resolve_connection(cls, connection, args, iterable, *nargs, **kwargs):
        # connectioon: NodeSetConnection
        # args: GraphQL Query
        # iterable: QuerySet

        connection = super().resolve_connection(
            connection, args, iterable, *nargs, **kwargs)

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


class BaseSerializerMutation(SerializerMutation):
    class Meta:
        abstract = True

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        client_mutation_id = input.get('client_mutation_id', None)
        if isinstance(client_mutation_id, str):
            _, id = from_global_id(client_mutation_id)
            input['id'] = id
        return super().get_serializer_kwargs(root, info, **input)
