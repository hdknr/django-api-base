from django.contrib.auth import get_user_model as USER, get_backends
from . import methods


User = USER()

User.all_permissions = methods.User.all_permissions
