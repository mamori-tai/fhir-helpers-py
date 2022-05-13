from typing import Any, List, Mapping, Union, Tuple

# from more_itertools import windowed


class PathError(Exception):
    ...


def _get_path_as_list(path: Union[str, List[str]]) -> List[str]:
    """
    Handle path, may be a string or a list of strings
    """
    return path.split(".") if isinstance(path, str) else list(path)


def _get_attribute_for_path(
    source: Mapping,
    /,
    path: List[str],
    default_defined: bool = False,
    default: Any = None,
) -> Tuple[Any, List[str]]:
    def return_or_raise(err_msg: str, e: Exception):
        if default_defined:
            return default, []
        raise PathError(err_msg) from e

    current = source
    sub_path = path[0]

    try:
        if sub_path.isnumeric():
            current = current[int(sub_path)]
        else:
            current = current.__getitem__(sub_path)
    except IndexError as e:
        return return_or_raise(f"Error accessing list index '{int(sub_path)}'", e)
    except KeyError as e:
        return return_or_raise(f"Error accessing dict item '{sub_path}'", e)
    path.pop(0)
    return current, path


def get_attribute_for_path(
    source_inst: Mapping, /, path: Union[str, List[str]], **kwargs
):
    """
    fast implementation of JMESpath, go fetch an attribute described by the path
    Params:
      path: str
      source_inst: dict
    """
    default_defined = "default" in kwargs
    default = default_defined and kwargs["default"] or None

    path_as_list = _get_path_as_list(path)
    if not path_as_list:
        return source_inst

    current_value, current_path = _get_attribute_for_path(
        source_inst, path_as_list, default_defined=default_defined, default=default
    )

    if not current_path:
        return current_value

    return get_attribute_for_path(current_value, current_path, **kwargs)


def get_attribute_for_path_gen(source_inst: Mapping, /, path: Union[str, List[str]]):

    current, path_as_list = _get_attribute_for_path(source_inst, path)

    if not path_as_list or current is None:
        return current, path_as_list

    if isinstance(current, list):
        for element in current:
            yield _get_attribute_for_path(element, path_as_list)
        path_as_list.pop(0)
    else:
        yield current, path_as_list

    yield from get_attribute_for_path_gen(current, path_as_list)


def set_attribute_for_path(target: Mapping, /, path: Union[str, List[str]], value: Any):
    """
    set a value in a dictionary given a path, meaning first path cannot be numeric
    Params:
      target: mapping in which the value will be set at the given path
      path: str or list of string
      value: the value to be set
    """
    if not path:
        return target

    path_as_list = _get_path_as_list(path)

    first = path_as_list[0]
    if first.isnumeric():
        raise ValueError("first item of the path can not be an integer")

    current = target

    for current_value, next_value in windowed(path_as_list, 2, step=1):
        # special case current numeric value
        if current_value.isnumeric():
            while int(current_value) >= len(current):
                current.append({})
            current = current[int(current_value)]
            # current = current[-1]
            continue

        # not in current
        if current_value not in current:
            if next_value is not None and next_value.isnumeric():
                current[current_value] = []
            else:
                current[current_value] = {}

        # if almost ended
        if next_value is None:
            continue

        # move forward
        current = current[current_value]

    # dealing with last value
    last = path_as_list[-1]
    if last.isnumeric():
        current.append(value)
    else:
        current[last] = value

    return target
