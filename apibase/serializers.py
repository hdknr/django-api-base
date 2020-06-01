from django.urls import reverse
from django.conf import settings
from rest_framework import fields, serializers
from .settings import apibase_settings
import traceback
import re


def to_urn(instance, service=None, nid=None):
    nid = nid or apibase_settings.URN_NID
    service = service or apibase_settings.HOST
    return f"urn:{nid}:{service}:{instance._meta.app_label}:{instance._meta.model_name}:{instance.pk}"


def endpoint_from_urn(urn, domain=None, scheme='https', nid=None, prefix='/api/rest'):
    nid = nid or apibase_settings.URN_NID
    domain = domain or  apibase_settings.DOMAIN
    ma = re.findall(r"([^:]+)", urn)
    if len(ma) == 6 and ma[0] == 'urn' and ma[1] == nid:
        return f"{scheme}://{ma[2]}.{domain}{prefix}/{ma[3]}/{ma[4]}/{ma[5]}/"
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
        instance = self.attr_name and getattr(value, self.attr_name, None) or value
        url = drf_endpoint(instance, url_name=self.get_url_name(value))
        request = self.context.get('request', None)
        return (request and url ) and request.build_absolute_uri(url) or url or None


class UrnField(fields.Field):

    def __init__(self, **kwargs):
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        self.attr_name = kwargs.get('attr_name', None)
        super().__init__(**kwargs) 

    def to_representation(self, value):
        instance = self.attr_name and getattr(value, self.attr_name, None) or value
        return to_urn(instance)


class BaseModelSerializer(serializers.ModelSerializer):
    endpoint = EndpointField()


class UrnModelSerializer(BaseModelSerializer):
    urn = UrnField()
