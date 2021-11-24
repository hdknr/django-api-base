from graphene.relay import Connection

from .mixins import SummaryMixin


class FilteringConnection(Connection, SummaryMixin):
    class Meta:
        abstract = True
