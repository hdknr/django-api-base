from logging import getLogger

import channels_graphql_ws

logger = getLogger()


class GraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
    """Channels WebSocket consumer which provides GraphQL API."""

    async def on_connect(self, payload):
        """New client connection handler."""
        logger.debug(f"on_connect ---------------{self.channel_name} {payload}")

    @classmethod
    def schema_consumer_class(cls, schema, name="SchemaWsConsumer"):
        return type(name, (cls,), {"schema": schema})


create_schema_consumer = GraphqlWsConsumer.schema_consumer_class
