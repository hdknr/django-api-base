from rest_framework import permissions
from functools import wraps
from logging import getLogger
logger = getLogger(__name__)


def has_perms(func, permission, *args, **kwargs):
    def wrapper(func):
        @wraps(func)
        def wrapped(self, info, *func_args, **func_kwargs):
            if not info.context.user.has_perm(permission):
                return None
            return func(self, info, *func_args, **func_kwargs)
        return wrapped
    return wrapper


class Permission(permissions.IsAuthenticated):
    PERM_CODE = None
    PRIVATE = True

    @classmethod
    def has(cls, func):
        @wraps(func)
        def wrapped(self, info, *func_args, **func_kwargs):
            if not cls.check_info(info, *func_args, **func_kwargs):
                return None
            return func(self, info, *func_args, **func_kwargs)
        return wrapped

    @classmethod
    def check_info(cls, info, *args, **kwargs):
        return info.context.user.has_perm(cls.PERM_CODE)

    def has_permission(self, request, view):
        if not request.user:
            return False

        isvalid = False if self.PRIVATE else (
            request.method in permissions.SAFE_METHODS)
        isvalid = isvalid or request.user.has_perm(self.PERM_CODE)
        if not isvalid:
            logger.info(f"{request.user} has not {self.PERM_CODE}")
        return isvalid
