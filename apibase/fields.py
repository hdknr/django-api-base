from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import SelectMultiple


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
