"""
https://django-filter.readthedocs.io/en/master/
"""

from apibase.filters import BaseFilter

from .. import models


class UserFilter(BaseFilter):
    class Meta:
        model = models.User
        exclude = [""]


class GroupFilter(BaseFilter):
    class Meta:
        model = models.Group
        exclude = [""]


class PermissionFilter(BaseFilter):
    class Meta:
        model = models.Permission
        exclude = [""]


class ContentTypeFilter(BaseFilter):
    class Meta:
        model = models.ContentType
        exclude = [""]
