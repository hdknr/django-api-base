from django.template import loader
from apibase.utils import query
from .utils import strip_relay
from django.contrib.contenttypes.models import ContentType


def query_model(model_or_instance, name=None, object_name=None, id=None, strip=True, **params):
    """
    Use .graphql files under django standard templates directories
    default:
        - query.graphql:  id is specifiled
        - query_set.graphql: id is not specified
    """
    if isinstance(model_or_instance, str):
        model_or_instance = ContentType.objects.get_by_natural_key(*model_or_instance.split(".")).model_class()

    opt = model_or_instance._meta
    object_name = object_name or opt.object_name
    if id or isinstance(model_or_instance, opt.model):
        name = name or "query"
        id = id or model_or_instance.id
    else:
        name = name or "query_set"

    template = f"{opt.app_label}/{opt.model_name}/{name}.graphql"
    source = loader.get_template(template).template.source
    data = query(source, object_name=object_name, id=id, **params)
    return strip and strip_relay(data, recursive=True) or data
