import functools
import uuid
from typing import Dict, Optional, TypeVar, Union, Any, Callable, cast

from fhir.resources.address import Address
from fhir.resources.careteam import CareTeam as FHIRCareTeam
from fhir.resources.condition import Condition as FHIRCondition
from fhir.resources.encounter import Encounter as FHIREncounter
from fhir.resources.fhirtypes import AddressType
from fhir.resources.flag import Flag as FHIRFlag
from fhir.resources.humanname import HumanName
from fhir.resources.list import List as FHIRList
from fhir.resources.observation import Observation as FHIRObservation
from fhir.resources.organization import Organization as FHIROrganization
from fhir.resources.patient import Patient as FHIRPatient
from fhir.resources.practitioner import Practitioner as FHIRPractitioner
from fhir.resources.questionnaireresponse import (
    QuestionnaireResponse as FHIRQuestionnaireResponse,
)
from fhir.resources.researchstudy import ResearchStudy as FHIRResearchStudy
from fhir.resources.researchsubject import ResearchSubject as FHIRResearchSubject
from fhir.resources.resource import Resource

# noinspection PyProtectedMember
from fn import _
from loguru import logger

from src.merger import merge
from src.utils import ilist, mixin

E = TypeVar("E", bound=Resource)


def get_attr(obj: E, attr_name: str, sub_attr: str, sub_attr_value: Any, index: int):
    if sub_attr_value:
        value = (
            ilist(getattr(obj, attr_name) or [])
            .filter(lambda x: getattr(x, sub_attr) == sub_attr_value)
            .safe_first
        )
        return value
    # fetch by index
    try:
        return getattr(obj, attr_name)[index]
    except (IndexError, TypeError):
        logger.error(f"No {attr_name=} found")
        return None


def get_identifier(obj: E, /, index: int = 0, system: str = None) -> Optional[str]:
    identifier_obj = get_attr(obj, "identifier", "system", system, index)
    return identifier_obj.value or "" if identifier_obj else None


def get_identifier_by_type(obj: E, /, system: str, code: str) -> Optional[str]:
    for ident in obj.identifier or []:
        type_ = ident.type
        if type_ is not None:
            codings = type_.coding or []
            for coding in codings:
                if coding.system == system and coding.code == code:
                    return ident.value or ""
    return None


def get_code(obj: E, /, index: int = 0) -> Optional[str]:
    try:
        return obj.code.coding[index]
    except (AttributeError, IndexError) as e:
        logger.error(e)
        return None


def get_extension(obj: E, /, index: int = 0, url: str = None):
    ext = get_attr(obj, "extension", "url", url, index)
    return ext


def get_telecom(
    obj: Union["Patient", "Practitioner"], system: str, use: Optional[str] = None
) -> str:
    if not system:
        raise ValueError(f"kind must be present, received {system=}")

    contacts = ilist(obj.telecom or [])
    # both use and system are defined
    predicate = (
        lambda c: c.system == system and c.use == use
        if use
        else lambda d: d.system == system
    )

    contact_point = contacts.filter(predicate).safe_first
    return contact_point.value or "" if contact_point else ""


def get_email(obj: Union["Patient", "Practitioner"]) -> str:
    return get_telecom(obj, "email")


def get_phone(obj: Union["Patient", "Practitioner"]) -> str:
    return get_telecom(obj, "phone")


def get_mobile(obj: Union["Patient", "Practitioner"]) -> str:
    return get_telecom(obj, "phone", "mobile")


def get_address(obj: Union["Patient", "Practitioner"]) -> Optional[AddressType]:
    return ilist(obj.address).safe_first


def get_formatted_address(obj: Union["Patient", "Practitioner"]) -> str:
    address = get_address(obj)
    if not address:
        return ""
    address = cast(Address, address)

    address_as_array = [
        " ".join(address.line or []) or "",
        address.postalCode or "",
        address.city or "",
        address.state or "FR",
    ]
    address_as_array = [
        address_part for address_part in address_as_array if address_part
    ]
    formatted_address = ", ".join(address_as_array)
    return formatted_address or address.text or ""


# name stuffs
def get_name(obj: Union["Patient", "Practitioner"], use=None) -> Optional[HumanName]:
    if not hasattr(obj, "name") or not obj.name:
        return None
    if not use:
        return ilist(obj.name or []).safe_first
    return ilist(obj.name or []).filter(_.use == use).safe_first


get_official_name = functools.partialmethod(get_name, use="official")
get_official_name.__name__ = "get_official_name"

get_usual_name = functools.partialmethod(get_name, use="usual")
get_usual_name.__name__ = "get_usual_name"

get_maiden_name = functools.partialmethod(get_name, use="maiden")
get_maiden_name.__name__ = "get_maiden_name"


def merge_with(obj: E, another_model: E, **kwargs: Any) -> E:
    if type(obj) != type(another_model):
        raise TypeError("Can only merge model of the same type")
    return obj.__class__(**merge(obj, another_model, **kwargs))


def find_contained_resource_with_matching_concept(
    obj: E, getter, systems: Dict[str, str]
) -> Optional[E]:
    for resource in getattr(obj, "contained", []):
        concepts = getter(resource)
        if not isinstance(concepts, list):
            concepts = [concepts]
        for concept in concepts:
            codings = concept.coding
            for coding in codings:
                value = systems.get(coding.system)
                if value is None:
                    continue
                if value == coding.code:
                    return resource


class MergeMixin:
    merge_with = merge_with


class CommonMixin(MergeMixin):
    get_identifier = get_identifier
    get_identifier_by_type = get_identifier_by_type
    get_extension = get_extension
    get_attr = get_attr
    get_code = get_code
    find_contained_resource_with_matching_concept = (
        find_contained_resource_with_matching_concept
    )


class PersonMixin(CommonMixin):
    get_email = get_email
    get_name = get_name
    get_official_name = get_official_name
    get_usual_name = get_usual_name
    get_maiden_name = get_maiden_name
    get_phone = get_phone
    get_telecom = get_telecom
    get_mobile = get_mobile
    get_address = get_address
    get_formatted_address = get_formatted_address


@mixin
class Patient(FHIRPatient, PersonMixin):
    ...


@mixin
class Practitioner(FHIRPractitioner, PersonMixin):
    ...


@mixin
class ResearchSubject(FHIRResearchSubject, CommonMixin):
    ...


@mixin
class QuestionnaireResponse(FHIRQuestionnaireResponse, CommonMixin):
    ...


@mixin
class Observation(FHIRObservation, CommonMixin):
    ...


@mixin
class Encounter(FHIREncounter, CommonMixin):
    ...


@mixin
class Condition(FHIRCondition, CommonMixin):
    ...


@mixin
class ResearchStudy(FHIRResearchStudy, CommonMixin):
    ...


@mixin
class Flag(FHIRFlag, CommonMixin):
    ...


@mixin
class Organization(FHIROrganization, CommonMixin):
    ...


@mixin
class CareTeam(FHIRCareTeam, CommonMixin):
    ...


@mixin
class List(FHIRList, CommonMixin):
    ...


@functools.lru_cache
def mixin_with(*fn: Callable[..., Any]):
    return type(f"{uuid.uuid4().hex}Mixin", (), {f.__name__: f for f in fn})
