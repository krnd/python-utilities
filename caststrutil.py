# pyright: reportUnusedImport=false

import typing
from typing import Any, Callable, Final, Sequence, Type, TypeVar


__version__ = "0.0.0"
__description__ = ""

__author__ = "Kilian Kaiping (krnd)"
__copyright__ = "Copyright (c) 2022 Kilian Kaiping (krnd)"
__license__ = "MIT"

__compatibility__ = "3.10"
__dependencies__ = ()
__utilities__ = ()

__all__ = (
    # fmt: off
    "NotResolved",
    "isnone", "isbool",
    "resolve"
    # fmt: on
)


T = TypeVar("T")
TB = TypeVar("TB", str, bool, int, float, bytes)


NONE_MAPPED_VALUES: Final = ("none", "null", "invalid")
FALSE_MAPPED_VALUES: Final = ("false", "no", "off", "disable", "disabled")
TRUE_MAPPED_VALUES: Final = ("true", "yes", "on", "enable", "enabled")

INT_BASE_INDICATORS: Final = {"b": 2, "o": 8, "x": 16}


SEQUENCE_SEP: Final = ","
SEQUENCE_NESTMAP: Final = {
    "(": ")",
    "[": "]",
    "{": "}",
}


class NotResolved(Exception):
    pass


def isnone(
    value: str | None,
    *,
    none: bool = True,
    empty: bool = True,
) -> bool:
    if value is None:
        return none
    elif len(value) == 0:
        return empty
    return value.lower() in NONE_MAPPED_VALUES


def isbool(
    value: str | None,
    *,
    none: bool = False,
    empty: bool = False,
) -> bool:
    if value is None:
        return none
    elif len(value) == 0:
        return empty
    return (
        value.lower() in FALSE_MAPPED_VALUES
        or value.lower() in TRUE_MAPPED_VALUES
    )


def resolve(valuestr: str, typehint: Type[T]) -> T:
    value: Any

    if typehint is Any:
        value = resolve_autodetect(valuestr)
        return value

    origin = typing.get_origin(typehint)
    if origin is None:
        value = resolve_builtin(valuestr, typehint)
    else:
        value = resolve_nested(
            valuestr,
            origin,
            typehint,
            _resolve=resolve,
        )

    return value


def resolve_autodetect(  # noqa: C901
    valuestr: str,
) -> None | bool | int | float | complex | bytes | str:
    if valuestr.lower() in NONE_MAPPED_VALUES:
        return None
    elif valuestr.lower() in FALSE_MAPPED_VALUES:
        return False
    elif valuestr.lower() in TRUE_MAPPED_VALUES:
        return True

    intbase = INT_BASE_INDICATORS.get(valuestr[1:2], 10)
    try:
        return int(valuestr, intbase)
    except ValueError:
        pass

    try:
        return float(valuestr)
    except ValueError:
        pass

    try:
        return complex(valuestr)
    except ValueError:
        pass

    try:
        return bytes.fromhex(valuestr)
    except ValueError:
        pass

    return str(valuestr)


def resolve_builtin(
    valuestr: str,
    typehint: Type[TB] | None,
) -> TB | None:
    if typehint is None:
        if valuestr.lower() in NONE_MAPPED_VALUES:
            return None
        raise ValueError(f"Value string '{valuestr}' not none.")

    elif typehint is str:
        return str(valuestr)  # type: ignore

    elif typehint is bool:
        if valuestr.lower() in FALSE_MAPPED_VALUES:
            return False  # type: ignore
        elif valuestr.lower() in TRUE_MAPPED_VALUES:
            return True  # type: ignore
        raise ValueError(f"Value string '{valuestr}' not bool.")

    elif typehint is int:
        intbase = INT_BASE_INDICATORS.get(valuestr[1:2], 10)
        return int(valuestr, intbase)  # type: ignore

    elif typehint is float:
        return float(valuestr)  # type: ignore

    elif typehint is bytes:
        return bytes.fromhex(valuestr)  # type: ignore

    raise Exception("invalid type")


def resolve_nested(
    valuestr: str,
    origin: type,
    typehint: Type[T],
    *,
    _resolve: Callable[[str, Type[T]], T],
) -> T:
    if origin is typing.Annotated:
        anntype, *_ = typing.get_args(typehint)
        return _resolve(valuestr, anntype)

    elif origin is typing.Union:
        raise NotImplementedError("caststrutil for union types")

    elif issubclass(origin, typing.List):
        (itemtype,) = typing.get_args(typehint)
        list_items = split_sequence(valuestr)
        return list(  # type: ignore
            _resolve(itemstr, itemtype) for itemstr in list_items
        )

    elif issubclass(origin, typing.Tuple):
        tuple_typehints = typing.get_args(typehint)
        if Ellipsis in tuple_typehints:
            (itemtype, _) = tuple_typehints
            tuple_items = split_sequence(valuestr)
            return tuple(  # type: ignore
                _resolve(itemstr, itemtype) for itemstr in tuple_items
            )
        else:
            raise Exception("=== TODO ===")
            expander = (
                tuple_typehints.index(str) if str in tuple_typehints else 0
            )
            tuple_items = split_sequence(
                valuestr, len(tuple_typehints), expander=expander
            )
            return tuple(  # type: ignore
                _resolve(itemstr, itemtype)
                for itemstr, itemtype in zip(tuple_items, tuple_typehints)
            )

    raise NotResolved()


def split_sequence(
    valuestr: str,
    *,
    sep: str = SEQUENCE_SEP,
    nestmap: dict[str, str] = SEQUENCE_NESTMAP,
) -> Sequence[str]:
    valuelist = list[str]()
    value = ""

    closestack = ""
    for ch in valuestr:
        if ch in nestmap:
            closestack += nestmap[ch]
        elif closestack and ch == closestack[-1]:
            closestack = closestack[:-1]
        elif not closestack and ch == sep:
            valuelist.append(value.strip())
            value = ""
            continue
        value += ch

    if value:
        valuelist.append(value.strip())
    return valuelist
