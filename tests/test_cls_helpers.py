from typing import Set

from assertpy.assertpy import assert_that
from loguru import logger
from pydantic import BaseModel

from src.cls_helpers import mixin_with, merge_with, Patient
from tests.resources.patient import patient1


class PatientProfile(BaseModel, mixin_with(merge_with)):
    name: str
    age: int = 0
    email: str = ""
    fields: Set[str] = {}


def test_mixin_with():
    patient_profile = PatientProfile(
        name="", email="toto@email.com", fields={"email"}
    ).merge_with(
        PatientProfile(name="Marc", age=12, email="", fields={"name", "age"}),
        fields_to_be_merged={"fields"},
    )
    assert_that(patient_profile).is_instance_of(PatientProfile)
    assert_that(patient_profile.name).is_equal_to("Marc")
    assert_that(patient_profile.age).is_equal_to(12)
    assert_that(patient_profile.email).is_equal_to("toto@email.com")
    assert_that(patient_profile.fields).contains("name", "age", "email")


def test_patient():
    patient = Patient(**patient1)
    assert_that(patient.get_name()).is_not_none()
    name = patient.get_name()
    assert_that(name.family).is_equal_to("DUBOIS")
    assert_that(name.given[0]).is_equal_to("Marc")
    assert_that(patient.get_email()).is_equal_to("cramm@hotmaill.fr")
