'''
https://django-filter.readthedocs.io/en/master/
'''
import django_filters
from django import forms
from django.db.models import Q, IntegerField
from functools import reduce
import operator
import re
import jaconv

class IntFilter(django_filters.NumberFilter):
    field_class = forms.IntegerField


class WordFilter(django_filters.CharFilter):

    def __init__(self, *args, lookups=[], delimiters=r'[\s\u3000,]+', **kwargs):
        self.lookups = lookups
        self.delimiters = delimiters
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value in django_filters.constants.EMPTY_VALUES:
            return qs

        vals = re.split(self.delimiters, value)
        vals = set(vals + [jaconv.zen2han(i) for i in vals])
        query = [
            reduce(operator.or_, [Q((f'{i}__contains', v))
                                  for i in self.lookups])
            for v in vals if v]

        qs = qs.filter(*query)
        if self.distinct:
            qs = qs.distinct()
        return qs


class BaseFilter(django_filters.FilterSet):
    pk = django_filters.NumberFilter(field_name='id')

    @classmethod
    def filter_for_lookup(cls, field, lookup_type):
        filter_class, param = super().filter_for_lookup(field, lookup_type)

        if lookup_type == 'exact' and filter_class == django_filters.ChoiceFilter:
            if isinstance(field, IntegerField):
                # print(field)
                filter_class = IntFilter
                param = {}

        return filter_class, param

    def filter_int(self, queryset, name, value):
        q = {name: int(round(value))}
        return queryset.filter(**q)
