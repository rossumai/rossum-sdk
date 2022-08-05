from dataclasses import dataclass

from rossum_api.models.parsing import dict_to_dataclass


@dataclass
class Foo:

    existing_field: str


def test_dict_to_dataclass():
    instance = dict_to_dataclass(Foo, {"existing_field": "value", "extra_field": "other-value"})
    assert instance == Foo("value")
