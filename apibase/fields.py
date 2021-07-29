import calendar
from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import SelectMultiple
from django_filters.fields import RangeField
from django_filters.widgets import DateRangeWidget


class ListCharField(forms.CharField):
    widget = SelectMultiple

    def to_python(self, value):
        if not value:
            return []
        elif not isinstance(value, (list, tuple)):
            raise ValidationError(
                self.error_messages["invalid_list"], code="invalid_list"
            )
        return [str(val) for val in value]


class MonthRangeField(RangeField):
    widget = DateRangeWidget

    def to_date(self, value, last=False):
        if value:
            ret = date(int(str(value)[:4]), int(str(value)[4:]), 1)
            if last:
                _, day = calendar.monthrange(ret.year, ret.month)
                return ret.replace(day=day)
            return ret

    def compress(self, data_list):
        data = data_list and [
            self.to_date(data_list[0]),
            self.to_date(data_list[1], last=True),
        ]
        if data:
            return slice(*data)
        return None
