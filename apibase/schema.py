import graphene.relay
# https://docs.graphene-python.org/projects/django/en/latest/queries/
from . import serializers
from graphene_django.filter import DjangoFilterConnectionField


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

            class Meta:
                node = self._type
                name = '{}NodeSetConnection'.format(self._type._meta.name)

            def resolve_total_count(self, info, **kwargs):
                return self.iterable.count()

        return NodeSetConnection