from typing import Any, List, Mapping, Union, Tuple, Dict


class PathError(Exception):
    ...


def _get_path_as_list(path: Union[str, List[str]]) -> List[str]:
    """
    Handle path, may be a string or a list of strings
    """
    if isinstance(path, list):
        r = []
        for p in path:
            if isinstance(p, str):
                r += p.split(".")
            else:
                r.append(p)
        return r
    return path.split(".")


def _get_attribute_for_path(
    source: Mapping,
    /,
    path: List[str],
    default_defined: bool = False,
    default: Any = None,
) -> Tuple[Any, List[Union[str, Mapping]]]:
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
    source_inst: Mapping, /, path: Union[str, List[Union[str, Mapping]]], **kwargs
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

    if (
        current_value
        and isinstance(current_value, List)
        and current_path
        and isinstance(current_path[0], Mapping)
    ):
        sub_path: Mapping = current_path.pop(0)
        current_value = _get_attribute_for_path_eq(
            current_value, *list(sub_path.items())[0], **kwargs
        )
        if current_value is None:
            if default_defined:
                return default
            raise PathError("No matching value found")

    if not current_path:
        return current_value

    return get_attribute_for_path(current_value, current_path, **kwargs)


def _get_attribute_for_path_eq(
    source: List[Mapping], path: Union[str, List[str]], value: Any, **kwargs
):
    for s in source:
        attr_value = get_attribute_for_path(s, path, **kwargs)
        if attr_value == value:
            return s
    return None


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

    if path_as_list[0].isnumeric():
        raise PathError("first item of the path can not be an integer")

    current = target

    skip = False

    for index in range(len(path_as_list) - 1):

        if skip is True:
            skip = False
            continue

        current_value, next_value = path_as_list[index], path_as_list[index + 1]
        # special case current numeric value
        if current_value.isnumeric():
            while int(current_value) >= len(current):
                current.append({})
            current = current[int(current_value)]
            continue

        # not in current
        if current_value not in current:
            if next_value.isnumeric():
                current[current_value] = []
            else:
                if isinstance(current, List):
                    raise PathError(
                        f"Got list instead of a dict...Wrong specified path {current_value=} ?"
                    )
                assert isinstance(current, Dict), "Unexpected error"
                current[current_value] = {}

        # move forward
        current = current[current_value]

        if isinstance(current, list) and isinstance(next_value, Mapping):
            current = _get_attribute_for_path_eq(current, *list(next_value.items())[0])
            skip = True

    # inserting last value
    last = path_as_list[-1]
    if last.isnumeric():
        current.append(value)
    else:
        current[last] = value

    return target


class _ObjectHandler:
    def __init__(self, obj: Dict[str, Any], path: List[Union[str, Mapping]], **kwargs):
        self.obj = obj
        self.path = path
        self.kwargs = kwargs


class _Updater(_ObjectHandler):
    def set(self, path: Union[str, List[str]], value: Any):
        return set_attribute_for_path(
            self.obj, self.path + _get_path_as_list(path), value
        )

    def append(self, value: Any):
        value_for_path = get_attribute_for_path(
            self.obj, path=self.path, **self.kwargs
        )
        if not isinstance(value_for_path, (list, set, tuple)):
            raise PathError(
                f"Can not add value to path {self.path=}, this is not an iterable"
            )

        if isinstance(value_for_path, list):
            value_for_path.append(value)
        elif isinstance(value_for_path, set):
            value_for_path.add(value)
        elif isinstance(value_for_path, tuple):
            set_attribute_for_path(
                self.obj,
                self.path,
                tuple([*list(value_for_path), value]),
            )
        return self.obj


class _Getter(_ObjectHandler):
    def get(self, path: Union[str, List[str]]):
        return get_attribute_for_path(
            self.obj, path=self.path + _get_path_as_list(path), **self.kwargs
        )


class _Finder:
    """ """

    def __init__(self, obj: Dict[str, Any], **kwargs):
        self.obj = obj
        self.path = []
        self.kwargs = kwargs

    def _update(self, path: Union[List[str], str], where: Dict[str, Any] = None):
        self.path += _get_path_as_list(path)
        if where is not None:
            self.path.append(where)

    def select(
        self, path: Union[List[str], str], where: Dict[str, Any] = None
    ) -> _Getter:
        self._update(path, where)
        return _Getter(self.obj, self.path, **self.kwargs)

    def update(
        self, path: Union[List[str], str], where: Dict[str, Any] = None
    ) -> _Updater:
        self._update(path, where)
        return _Updater(self.obj, self.path)


# alias
finder = _Finder


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
