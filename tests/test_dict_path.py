from assertpy import assert_that
from loguru import logger

from src.dict_path import (
    get_attribute_for_path as attr_for_path,
    PathError,
    set_attribute_for_path,
    finder,
)

dol = {"label": "doliprane"}
dol2 = {"medication": {"ingredients": ["paracétamol"]}}
dol3 = {
    "medication": {
        "ingredients": [
            {"extension": {"url": "1", "value": "1"}},
            {"extension": {"url": "2", "value": "2"}},
            {"extension": {"url": "3", "value": "3"}},
        ]
    }
}


def test_get_attribute_simple():
    assert_that(attr_for_path(dol, path="label")).is_equal_to("doliprane")


def test_get_attribute_nested():
    assert_that(
        attr_for_path(
            dol2,
            path="medication.ingredients.0",
        )
    ).is_equal_to("paracétamol")
    assert_that(attr_for_path).raises(PathError).when_called_with(
        dol2, path="medication.ingredients.1"
    )


def test_filtering():
    assert_that(
        attr_for_path(
            dol3, ["medication.ingredients", {"extension.url": "1"}, "extension.value"]
        )
    ).is_equal_to("1")

    assert_that(
        attr_for_path(
            dol3,
            ["medication.ingredients", {"extension.url": "4"}, "extension.value"],
            default=None,
        )
    ).is_none()

    assert_that(attr_for_path).raises(PathError).when_called_with(
        dol3, ["medication.ingredients", {"extension.url": "4"}, "extension.value"]
    )


def test_higher_level_api():
    assert_that(
        finder(dol3)
        .select("medication.ingredients", where={"extension.url": "1"})
        .get("extension.value")
    ).is_equal_to("1")

    assert_that(
        finder({**dol3})
        .update("medication.ingredients", where={"extension.url": "1"})
        .set("extension.value", "8")
    ).is_equal_to(
        {
            "medication": {
                "ingredients": [
                    {"extension": {"url": "1", "value": "8"}},
                    {"extension": {"url": "2", "value": "2"}},
                    {"extension": {"url": "3", "value": "3"}},
                ]
            }
        }
    )


def test_set_attribute_simple():
    result = set_attribute_for_path({}, path="medication.label", value="doliprane")
    assert_that(result).is_equal_to({"medication": {"label": "doliprane"}})


def test_set_attribute_list():
    result = set_attribute_for_path({}, path="medication.label.0", value="doliprane")
    assert_that(result).is_equal_to({"medication": {"label": ["doliprane"]}})


def test_set_attribute_list_second():
    result = set_attribute_for_path(
        {}, path="medication.label.0.ingredient.form", value="comprimé"
    )
    assert_that(result).is_equal_to(
        {"medication": {"label": [{"ingredient": {"form": "comprimé"}}]}}
    )


def test_set_attribute_list_third():
    result = set_attribute_for_path(
        {}, path="medication.label.0.ingredient.form.dosage", value="125mg"
    )
    assert_that(result).is_equal_to(
        {"medication": {"label": [{"ingredient": {"form": {"dosage": "125mg"}}}]}}
    )


def test_raise_when_set_attribute_integer():
    assert_that(set_attribute_for_path).raises(ValueError).when_called_with(
        {}, path="0.label.0.ingredient.form", value="comprimé"
    )


def test_set_attribute_with_dict():
    dol4 = {**dol3}
    assert_that(
        set_attribute_for_path(
            dol4,
            ["medication.ingredients", {"extension.url": "1"}, "extension.value"],
            "8",
        )
    ).is_equal_to(
        {
            "medication": {
                "ingredients": [
                    {"extension": {"url": "1", "value": "8"}},
                    {"extension": {"url": "2", "value": "2"}},
                    {"extension": {"url": "3", "value": "3"}},
                ]
            }
        }
    )
