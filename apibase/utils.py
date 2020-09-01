import six

from django_filters.utils import get_model_field
from django_filters.filters import RangeFilter 
from graphene_django.forms.converter import convert_form_field
from graphql_relay.connection.arrayconnection import get_offset_with_default
from gql import gql, Client


def get_filtering_args_from_filterset(filterset_class, type, obvious_filters=[]):
    '''
    Original:
        - https://github.com/graphql-python/graphene-django/blob/master/graphene_django/filter/utils.py#L7
        - filters not in 'declared_filters' are defined by Graphene-Django for model fields `formfield`.

    obivius_filters:
        - Force to use field class defined in filters.
    '''

    args = {}
    model = filterset_class._meta.model
    for name, filter_field in six.iteritems(filterset_class.base_filters):
        form_field = None

        if name in filterset_class.declared_filters:
            form_field = filter_field.field
        elif filter_field.__class__ in obvious_filters:
            form_field = filter_field.field
        else:
            model_field = get_model_field(model, filter_field.field_name)
            filter_type = filter_field.lookup_expr
            if filter_type != "isnull" and hasattr(model_field, "formfield"):
                form_field = model_field.formfield(
                    required=filter_field.extra.get("required", False)
                )

        # Fallback to field defined on filter if we can't get it from the
        # model field
        if not form_field:
            form_field = filter_field.field

        field_type = convert_form_field(form_field).Argument()
        field_type.description = filter_field.label

        # For RangeFilter, duplicate filter args for suffixes
        if isinstance(filter_field, RangeFilter) and hasattr(filter_field.field, 'widget'):
            suffixes = getattr(filter_field.field.widget, 'suffixes', []) 
            for s in suffixes:
                if s: 
                    args[f"{name}_{s}"] = field_type
        else:
            args[name] = field_type

    return args


def resolve_start_offset(slice_start, after):
    after_offset = get_offset_with_default(after, -1)
    return  max(slice_start - 1, after_offset, -1) + 1


def gql_query(schema, query_str, **params):
    client = Client(schema=schema)
    query = gql(query_str)
    return client.execute(query, variable_values=params)
