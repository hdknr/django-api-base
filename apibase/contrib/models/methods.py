from django.contrib import auth


def all_permissions(self):
    permissions = set()
    for backend in auth.get_backends():
        if hasattr(backend, "get_all_permissions"):
            permissions.update(backend.get_all_permissions(self))
    return permissions


User = type("User", (), {"all_permissions": all_permissions})
