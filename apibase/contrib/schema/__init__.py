from logging import getLogger

import graphene
from apibase.utils import gql_query

from . import query

logger = getLogger()


class Query(
    query.Query,
):
    pass


schema = graphene.Schema(
    query=Query,
    auto_camelcase=False,
)


def exec_query(query_string, **params):
    return gql_query(schema, query_string, **params)
