import json
from pathlib import Path

import yaml
from django.apps import apps
from factory import fuzzy as FZ
from gql import gql
from graphql import print_ast

from apibase.utils import query


def get_test_fixture(name, app_label=None, base=None):
    """(app_label/tests/fixtures/name)"""
    path = Path(apps.get_app_config(app_label).path) if app_label else Path(base)
    return str(path.joinpath(f"tests/fixtures/{name}"))


def load_test_fixture(name, app_label=None, base=None):
    path = get_test_fixture(name, app_label=app_label, base=base)
    suffix = Path(path).suffix
    if suffix in [".json"]:
        return json.load(open(path))
    elif suffix in [".yml", ".yaml"]:
        return yaml.load(open(path), Loader=yaml.FullLoader)
    return open(path).read()


def strip_relay(obj, recursive=False):
    if isinstance(obj, list):
        return [strip_relay(i, recursive=recursive) for i in obj]

    if isinstance(obj, dict):
        if "edges" in obj:
            if not recursive:
                return [i["node"] for i in obj["edges"]]
            return [strip_relay(i["node"], recursive=recursive) for i in obj["edges"]]

        return dict((k, strip_relay(v, recursive=recursive)) for k, v in obj.items())
    return obj


class FixtureMixin:
    @classmethod
    def fuzzychoice(cls, *args, **kwargs):
        return FZ.FuzzyChoice(cls.qs().filter(*args, **kwargs))

    @classmethod
    def get_app_label(cls):
        return cls.__module__.split(".")[0]

    @classmethod
    def fixture(cls, name):
        app_label = cls.get_app_label()
        return get_test_fixture(f"{name}", app_label=app_label)

    @classmethod
    def load_fixture(cls, name):
        app_label = cls.get_app_label()
        return load_test_fixture(f"{name}", app_label=app_label)

    @classmethod
    def graphql_query(cls, name):
        return print_ast(gql(open(cls.fixture(name)).read()))

    @classmethod
    def gql(cls, id=None, strip_recursive=False, **params):
        """
        id : app_label/tests/fixtures/{model_name}.graphql
        not id : app_label/tests/fixtures/{model_name}_set.graphql
        """
        object_name = cls._meta.model._meta.object_name

        if id:
            name = f"{object_name}".lower()
            kwargs = {"object_name": object_name, "id": id, **params}
        else:
            name = f"{object_name}_set".lower()
            kwargs = {**params}

        data = query(cls.load_fixture(f"{name}.graphql"), **kwargs)[name]

        if strip_recursive:
            return strip_relay(data, recursive=strip_recursive)
        return data

    @classmethod
    def from_json(cls, name):
        return json.load(open(cls.fixture(name)))

    @classmethod
    def qs(cls):
        return cls._meta.model.objects

    @classmethod
    def from_fixture(cls, name, listkey="items", **kwargs):
        fixture = cls.load_fixture(name)
        model_name = cls._meta.model._meta.model_name
        if listkey in fixture:
            return list(map(lambda i: cls.create(**{**i[model_name], **kwargs}), fixture[listkey]))
        else:
            return cls.create(**{**fixture[model_name], **kwargs})

    @classmethod
    def create_from_list(cls, items, **params):
        return list(map(lambda i: cls.create(**params, **i), items))
