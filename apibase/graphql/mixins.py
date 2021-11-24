import graphene.relay

from .. import serializers


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
        if hasattr(info.context, "build_absolute_uri"):
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
