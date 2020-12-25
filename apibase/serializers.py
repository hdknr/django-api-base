from django.urls import reverse
from django.db.models import Model
from django.db.models.fields.reverse_related import OneToOneRel
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import fields, serializers
from rest_framework.fields import empty
from .settings import apibase_settings
import re


def to_urn(instance, nss=None, nid=None):
    nid = nid or apibase_settings.URN_NID
    nss = nss or apibase_settings.URN_NSS
    return f"urn:{nid}:{nss}:{instance._meta.app_label}:{instance._meta.model_name}:{instance.pk}"


def endpoint_from_urn(urn, domain=None, nid=None, prefix='/api/rest', request=None):
    nid = nid or apibase_settings.URN_NID
    domain = domain or apibase_settings.DOMAIN or get_current_site(
        request).domain
    ma = re.findall(r"([^:]+)", urn)
    if len(ma) == 6 and ma[0] == 'urn' and ma[1] == nid:
        if ma[2] == 'self':
            service = ''
        else:
            _, domain = re.search(r'(?:([^\.]+)\.)?(.+)', domain).groups()
            service = ma[2] + "."
        return f"{apibase_settings.SCHEME}://{service}{domain}{prefix}/{ma[3]}/{ma[4]}/{ma[5]}/"
    return None


def drf_endpoint(instance, url_name=None, pk_name='pk'):
    ''' DRF endpoint '''
    try:
        if hasattr(instance, 'get_endpoint_url'):
            return instance.get_endpoint_url()
        name = url_name or f"api-{instance._meta.app_label}-{instance._meta.model_name}-detail"
        return reverse(name, kwargs={pk_name: instance.pk})
    except:
        pass
    return ''


class EndpointField(fields.Field):

    def __init__(self, **kwargs):
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        self.url_name = kwargs.get('url_name', None)
        self.attr_name = kwargs.get('attr_name', None)
        super().__init__(**kwargs)

    def get_url_name(self, value):
        return self.url_name

    def to_representation(self, value):
        instance = self.attr_name and getattr(
            value, self.attr_name, None) or value
        url = drf_endpoint(instance, url_name=self.get_url_name(value))
        request = self.context.get('request', None)
        return (request and url) and request.build_absolute_uri(url) or url or None


class UrnField(fields.Field):

    def __init__(self, **kwargs):
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        self.attr_name = kwargs.get('attr_name', None)
        super().__init__(**kwargs)

    def to_representation(self, value):
        instance = self.attr_name and getattr(
            value, self.attr_name, None) or value
        return to_urn(instance)


class DisplayField(fields.Field):

    def __init__(self, **kwargs):
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        self.attr_name = kwargs.get('attr_name', None)
        super().__init__(**kwargs)

    def to_representation(self, value):
        instance = self.attr_name and getattr(
            value, self.attr_name, None) or value
        return str(instance)


class BaseModelSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    endpoint = EndpointField()
    urn = UrnField()
    display = DisplayField()

    nested_fields = []

    def to_representation(self, instance):
        '''(override)'''
        data = super().to_representation(instance)
        if hasattr(self, 'patch_result'):
            self.patch_result(instance, data)
        return data

    def run_validation(self, data=empty):
        '''(override)'''
        self._children_set = dict((i, data.pop(i, None))
                                  for i in self.nested_fields)
        return super().run_validation(data=data)

    @classmethod
    def update_or_create(cls, partial=None, id=None, **validated_data):
        instance = id and cls.Meta.model.objects.filter(id=id).first()
        serializer = cls(instance=instance,
                         data=validated_data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

    def patch_children(self, instance, field_name, data):
        return data

    def update_nested(self, instance, validated_data, field_name, children):
        if not children or not instance:
            return

        name = re.sub(r'(.+)(_set)$', r'\g<1>', field_name)
        related_field = self.Meta.model._meta.get_field(name)
        remote_field_name = related_field.remote_field.name
        if isinstance(related_field, OneToOneRel):
            children = [children]
            ser = self.fields[field_name]
        else:
            ser = self.fields[field_name].child

        for item in children:
            item[remote_field_name] = instance.id
            for key in item:
                if isinstance(item[key], Model):
                    # prevent serilizer.is_valid() -> False
                    item[key] = item[key].id

            data = self.patch_children(instance, field_name, item)
            ser.update_or_create(partial=self.partial, **data)

    def update_nested_fields(self, instance, validated_data, children_set):
        for field_name, children in children_set.items():
            self.update_nested(instance, validated_data, field_name, children)

    def validated_children_set(self, validated_data):
        children_set = getattr(self, '_children_set', [])
        children_set = children_set or \
            dict((i, validated_data.pop(i, [])) for i in self.nested_fields)
        return children_set

    def update(self, instance, validated_data):
        children_set = self.validated_children_set(validated_data)
        self.update_nested_fields(instance, validated_data, children_set)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        children_set = self.validated_children_set(validated_data)
        instance = super().create(validated_data)
        self.update_nested_fields(instance, validated_data, children_set)
        return instance


class UrnModelSerializer(BaseModelSerializer):
    urn = UrnField()
