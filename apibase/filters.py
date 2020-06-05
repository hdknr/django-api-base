'''
https://django-filter.readthedocs.io/en/master/
'''
import django_filters
from django.db.models import Q
from functools import reduce
import operator
import re


class WordFilter(django_filters.CharFilter):

    def __init__(self, *args, lookups=[], delimiters=r'[\s\u3000,]+', **kwargs):
        self.lookups = lookups
        self.delimiters = delimiters
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value in django_filters.constants.EMPTY_VALUES:
            return qs

        vals = re.split(self.delimiters, value)
        query = [
            reduce(operator.or_, [Q((f'{i}__contains', v)) for i in self.lookups])
            for v in vals if v]

        qs = qs.filter(*query)
        if self.distinct:
            qs = qs.distinct()
        return qs


class BaseFilter(django_filters.FilterSet):
    pk = django_filters.NumberFilter(field_name='id')

    def filter_int(self, queryset, name, value):
        q = {name: int(round(value))}
        return queryset.filter(**q)
