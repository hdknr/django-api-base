from django.contrib.auth import get_backends
from django.contrib.auth import get_user_model as USER

from . import methods

User = USER()

User.all_permissions = methods.User.all_permissions
