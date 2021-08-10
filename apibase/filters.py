"""
https://django-filter.readthedocs.io/en/stable/
"""
import operator
import re
from functools import reduce

import django_filters
import jaconv
from django import forms
from django.db.models import IntegerField, Q

from .fields import ListCharField, MonthRangeField


class IntFilter(django_filters.NumberFilter):
    field_class = forms.IntegerField


SPACES = r"[\s\u3000,]+"


class WordFilter(django_filters.CharFilter):
    def __init__(self, *args, lookups=None, delimiters=None, **kwargs):
        self.lookups = lookups or []
        self.delimiters = delimiters or SPACES
        kwargs["lookup_expr"] = kwargs.get("lookup_expr", "contains")
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value in django_filters.constants.EMPTY_VALUES:
            return qs

        def _q(lookup, val):
            key = f"{lookup}__{self.lookup_expr}"
            val2 = jaconv.zen2han(val)
            if val2 == val:
                return Q((key, val))
            return Q((key, val)) | Q((key, val2))

        vals = re.split(self.delimiters, value)
        query = [reduce(operator.or_, [_q(i, v) for i in self.lookups]) for v in vals if v]

        qs = qs.filter(*query)
        if self.distinct:
            qs = qs.distinct()
        return qs


class BaseFilter(django_filters.FilterSet):
    pk = django_filters.NumberFilter(field_name="id")

    @classmethod
    def filter_for_lookup(cls, field, lookup_type):
        filter_class, param = super().filter_for_lookup(field, lookup_type)

        if lookup_type == "exact" and filter_class == django_filters.ChoiceFilter:
            if isinstance(field, IntegerField):
                # print(field)
                filter_class = IntFilter
                param = {}

        return filter_class, param

    def filter_int(self, queryset, name, value):
        q = {name: int(round(value))}
        return queryset.filter(**q)


class AllValuesMultipleFilter(django_filters.AllValuesMultipleFilter):
    # field_class: django_filters.fields.MultipleChoiceField

    @property
    def field(self):
        # not cache as '_field' to work with `choices`
        if hasattr(self, "model"):
            qs = self.model._default_manager.distinct()
            qs = qs.order_by(self.field_name).values_list(self.field_name, flat=True)
            self.extra["choices"] = [(o, o) for o in qs]
        field_kwargs = self.extra.copy()
        return self.field_class(label=self.label, **field_kwargs)

    def get_filter_predicate(self, v):
        # 'field_name' MUST BE endswith "__in"
        return {f"{self.field_name}__in": v}


class ListCharInFilter(django_filters.CharFilter):
    field_class = ListCharField

    def get_filter_predicate(self, v):
        return {f"{self.field_name}__in": v}

    def filter(self, qs, values):
        if not values:
            return qs

        predicate = self.get_filter_predicate(values)
        qs = self.get_method(qs)(**predicate)
        return qs.distinct() if self.distinct else qs


class MonthFromToRangeFilter(django_filters.RangeFilter):
    field_class = MonthRangeField


class RelatedFilterSetMixin:
    @classmethod
    def create_related_filterset(cls, related_name):
        fields = dict(
            (
                f"{related_name}__{key}",
                instance.__class__(label=instance.label, field_name=f"{related_name}__{instance.field_name}"),
            )
            for key, instance in cls.declared_filters.items()
        )
        return type(f"RelatedFilter_{related_name}", (django_filters.FilterSet,), fields)
