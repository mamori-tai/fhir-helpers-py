from operator import itemgetter
from typing import Optional, Any, NoReturn, Union, List

last_func = itemgetter(-1)
first_func = itemgetter(0)

last = last_func
first = first_func


class IList(list):
    last = property(lambda self: last_func(self))
    first = property(lambda self: first_func(self))

    def append(self, value) -> NoReturn:
        raise AttributeError("Could not append")

    @property
    def is_empty(self) -> bool:
        return len(self) == 0

    @property
    def safe_first(self) -> Optional[Any]:
        if not self:
            return None
        return self.first

    def filter(self, predicate) -> "IList":
        return IList([x for x in self if predicate(x)])

    def map_to(self, function) -> "IList":
        return IList([function(x) for x in self])

    def __iadd__(self, value):
        raise AttributeError("Could not add in place")

    def __or__(self, value: Any) -> "IList":
        new_list = self[:]
        if isinstance(value, list):
            new_list += value
            return IList(new_list)
        new_list.append(value)
        return IList(new_list)


def ilist(*a_list):
    if len(a_list) == 1:
        if not isinstance(a_list[0], (list, set)):
            raise ValueError("")
        return IList(a_list[0])
    return IList(a_list)


def to_list(values: Union[List[Any], Any]) -> List[Any]:
    if isinstance(values, list):
        return values
    return [values]


def mixin(cls):
    return cls
