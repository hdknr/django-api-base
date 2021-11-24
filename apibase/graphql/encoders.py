import decimal

from django.core.serializers.json import DjangoJSONEncoder


class JSONEncode(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, (decimal.Decimal)):
            return float(o)

        return super().default(o)
