from typing import Any, List


class DotDict(dict):
    """
    The `DotDict` class allows accessing items in a dict using a
    dot syntax.

    >>> dotdict = DotDict({"a":{"b":"hello"}})
    >>> dotdict.a.b
    'hello'
    """

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, init_data={}):
        assert isinstance(init_data, dict)
        for key, value in init_data.items():
            if hasattr(value, "keys"):
                if isinstance(value, DotDict):
                    self[key] = value
                else:
                    self[key] = DotDict(value)
            else:
                self[key] = value

    def as_dict(self) -> dict:
        """
        Converts the DotDict into a python `dict` recursively.

        >>> dotdict = DotDict({"a": {"b": {"c": [0, DotDict({"d": 1})]}}})
        >>> type(dotdict)
        <class 'datatypes.DotDict'>
        >>> type(dotdict.a.b.c[1])
        <class 'datatypes.DotDict'>
        >>> as_dict = dotdict.as_dict()
        >>> type(as_dict)
        <class 'dict'>
        >>> type(as_dict["a"]["b"]["c"][1])
        <class 'dict'>
        """

        def convert(value: Any) -> Any:
            if isinstance(value, DotDict):
                return value.as_dict()
            elif isinstance(value, list):
                return list(map(convert, value))
            else:
                return value

        return {key: convert(value) for key, value in self.items()}