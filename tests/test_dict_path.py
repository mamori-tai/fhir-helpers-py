from assertpy import assert_that
from loguru import logger

from src.dict_path import get_attribute_for_path as attr_for_path, PathError

dol = {"label": "doliprane"}
dol2 = {"medication": {"ingredients": ["paracétamol"]}}


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


# def test_set_attribute_simple():
#     result = set_attribute_for_path({}, path="medication.label", value="doliprane")
#     self.assertDictEqual(result, {"medication": {"label": "doliprane"}})
#
# def test_set_attribute_list():
#     result = set_attribute_for_path(
#         {}, path="medication.label.0", value="doliprane"
#     )
#     self.assertDictEqual(result, {"medication": {"label": ["doliprane"]}})
#
# def test_set_attribute_list_second():
#     result = set_attribute_for_path(
#         {}, path="medication.label.0.ingredient.form", value="comprimé"
#     )
#     self.assertDictEqual(
#         result, {"medication": {"label": [{"ingredient": {"form": "comprimé"}}]}}
#     )
#
# def test_raise_when_set_attribute_integer():
#     with self.assertRaises(ValueError):
#         set_attribute_for_path(
#             {}, path="0.label.0.ingredient.form", value="comprimé"
#         )
#
