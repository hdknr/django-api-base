'''
https://django-filter.readthedocs.io/en/master/
'''
import django_filters


class BaseFilter(django_filters.FilterSet):
    pk = django_filters.NumberFilter(field_name='id')

    def filter_int(self, queryset, name, value):
        q = {name: int(round(value))}
        return queryset.filter(**q)
