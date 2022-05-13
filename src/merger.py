from typing import Mapping, Union

from pydantic import BaseModel


def merge(
    resource1: Union[BaseModel, Mapping], resource2: Union[BaseModel, Mapping], **kwargs
):
    by_alias = kwargs.get("by_alias", True)
    fields_to_be_merged = kwargs.get("fields_to_be_merged", {})

    resource1_as_dict = (
        resource1.dict(by_alias=by_alias)
        if isinstance(resource1, BaseModel)
        else resource1
    )
    resource2_as_dict = (
        resource2.dict(by_alias=by_alias)
        if isinstance(resource2, BaseModel)
        else resource2
    )

    new_dict = {}

    if not resource1_as_dict:
        return {}

    for key, value in resource1_as_dict.items():
        resource2_value = resource2_as_dict.get(key)

        # handle special cases for this one
        if key in fields_to_be_merged:
            new_dict[key] = list(set(value or []) | set(resource2_value or []))
            continue

        # handle normal case
        if not isinstance(value, Mapping):
            new_dict[key] = resource2_value or value
        else:
            new_dict[key] = merge(value, resource2_value or {})

    return new_dict
