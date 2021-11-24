import json

import graphene
from django.db.models import QuerySet
from graphene.relay import Connection
from graphene.types import generic

from .encoders import JSONEncode


class FilteringConnection(Connection):
    total_count = graphene.Int()
    records = graphene.Int()
    summary = generic.GenericScalar()

    class Meta:
        abstract = True

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
