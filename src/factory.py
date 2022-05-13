# factory
from typing import Union, List
from uuid import uuid4

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.extension import Extension
from fhir.resources.identifier import Identifier
from fhir.resources.reference import Reference

from src.enum import TermURL


def codeable_concept(
    codings: Union[List[Coding], Coding], /, text: str = None
) -> CodeableConcept:
    """factory for codeable concept"""
    if isinstance(codings, Coding):
        codings = [codings]
    return CodeableConcept(coding=codings, text=text)


def identifier(
    value: Union[Identifier, List[Identifier]] = None, /, as_list=False
):  # pragma: no cover
    if isinstance(value, list):
        return value
    if value is None:
        identifier_obj = Identifier(value=str(uuid4().urn))
        return [identifier_obj] if as_list else identifier_obj
    if value.value is None:
        value.value = str(uuid4())
    return [value] if as_list else value


def extension(system=TermURL.SYNAPSE, /, **kwargs):  # pragma: no cover
    """factory for extension"""
    ext = Extension(url=system.value, **kwargs)
    if kwargs["as_list"]:
        return [ext]
    return ext


def ref(
    reference: str, /, as_list=False
) -> Union[List[Reference], Reference]:  # pragma: no cover
    reference_obj = Reference(reference=reference)
    if as_list:
        return [reference_obj]
    return reference_obj
