import os
import uuid
from pathlib import Path

from base.utils import dates
from django.contrib.contenttypes.models import ContentType
from django.utils.deconstruct import deconstructible


@deconstructible
class UploadPathResolver:
    """ file upload resolver
    """

    def __init__(self, field_name, access=""):
        self.field_name = field_name
        self.access = access
        self.content_type = None

    def __call__(self, instance, filename):
        self.content_type = self.resolve_content_type(instance)
        #
        filename = self.create_path(filename, instance=instance)
        filename = self.construct_filename(instance, filename)
        return self.on_resolve_filename(instance, filename) or filename

    def on_resolve_filename(instance, app_label, model_name, filename):
        return None

    def create_path(self, filename, **kwargs):
        path = Path(filename)
        today = dates.now().strftime("%Y-%m-%d")
        return "%s/%s%s" % (today, uuid.uuid4(), path.suffix)

    def resolve_content_type(self, instance):
        return (
            self.content_type or getattr(instance, "content_type", None) or ContentType.objects.get_for_model(instance)
        )

    def construct_filename(self, instance, path):
        content_type = self.resolve_content_type(instance)
        return os.path.join(self.access, content_type.app_label, content_type.model, self.field_name, path)

    def find_instance(self, model_class, path):
        query = {self.field_name: self.construct_filename(model_class(), path)}
        return model_class.objects.filter(**query).first()

    @classmethod
    def find(cls, model_class, field_name, path):
        field = model_class._meta.get_field(field_name)
        return field and field.upload_to.find_instance(model_class, path) or None
