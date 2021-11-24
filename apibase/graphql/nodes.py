from graphene.relay import Node

from .fields import NodeSet


class FilteringNode(Node):
    @classmethod
    def Field(cls, *args, **kwargs):  # noqa: N802
        return NodeSet(cls, *args, **kwargs)  # NodeField を返している
