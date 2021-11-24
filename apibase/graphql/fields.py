import json

import graphene.relay
from django.db.models import QuerySet
from graphene.types import generic

# https://docs.graphene-python.org/projects/django/en/latest/queries/
from graphene_django.filter import DjangoFilterConnectionField

from .. import filters, utils
from .encoders import JSONEncode


class NodeSet(DjangoFilterConnectionField):
    # https://github.com/graphql-python/graphene-django/issues/320#issuecomment-404802724

    def __init__(self, *args, **kwargs):
        name_prefix = kwargs.pop("name_prefix", "")
        super().__init__(*args, **kwargs)
        self.name_prefix = name_prefix

    @property
    def type(self):
        class NodeSetConnection(graphene.Connection):
            total_count = graphene.Int()
            records = graphene.Int()
            summary = generic.GenericScalar()

            class Meta:
                node = self._type
                name = "{}{}NodeSetConnection".format(self.name_prefix, self._type._meta.name)

            def resolve_total_count(self, info, **kwargs):
                return self.length

            def resolve_summary(self, info, **kwargs):
                if isinstance(self.iterable, QuerySet) and hasattr(self.iterable, "summary"):
                    data = json.dumps(self.iterable.summary(), cls=JSONEncode)
                    return json.loads(data)
                return None

            def resolve_records(self, info, **kwargs):
                if isinstance(self.iterable, QuerySet):
                    # TODO: each models may have it own countable criteria
                    return self.iterable.order_by("id").distinct().count()

                return self.length

        return NodeSetConnection

    @classmethod
    def resolve_connection(cls, connection, args, iterable, *nargs, **kwargs):
        # connectioon: NodeSetConnection
        # args: GraphQL Query
        # iterable: QuerySet

        connection = super().resolve_connection(connection, args, iterable, *nargs, **kwargs)

        start_offset = utils.resolve_start_offset(0, args.get("after"))
        connection.page_info.has_previous_page = start_offset > 0

        return connection

    obvious_filters = [
        filters.IntFilter,
    ]

    @property
    def filtering_args(self):
        return utils.get_filtering_args_from_filterset(
            self.filterset_class, self.node_type, obvious_filters=self.obvious_filters
        )

    @classmethod
    def resolve_queryset(cls, connection, iterable, info, args, filtering_args, filterset_class):
        qs = super().resolve_queryset(connection, iterable, info, args, filtering_args, filterset_class)
        # duplicated result when related models are filtered
        return qs.distinct()
