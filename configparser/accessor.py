from configparser import ConfigParser
from typing import (
    Final,
    Iterable,
    Literal,
    Mapping,
    Sequence,
    Type,
    TypeVar,
    overload,
)

from arborister.utilities import caststrutil
from arborister.utilities.symbol import Symbol


__version__ = "0.0.0"
__description__ = ""

__author__ = "Kilian Kaiping (krnd)"
__copyright__ = "Copyright (c) 2022 Kilian Kaiping (krnd)"
__license__ = "MIT"

__compatibility__ = "3.10"
__dependencies__ = ()
__utilities__ = ("caststrutil", "symbol")


T = TypeVar("T")


DEFAULT_LISTSEP: Final = ","


class _NoValue(Symbol):
    pass


class ConfigParserAccessor:

    variables: Mapping[str, str]

    scope: str | None

    def __init__(
        self,
        source: ConfigParser,
        variables: Mapping[str, str] | None = None,
        *,
        scope: str | None = None,
        listsep: str = DEFAULT_LISTSEP,
        repack_variables: bool = True,
    ) -> None:
        self._source = source

        if variables and repack_variables:
            variables = dict(variables)
        self.variables = variables or {}

        self.scope = scope

        self._listsep = listsep

    @property
    def configparser(self) -> ConfigParser:
        return self._source

    @overload
    def get(
        self,
        option: str,
        typecast: Type[T],
        default: None = ...,
        *,
        section: str | None = ...,
        recurse: Literal[False] = ...,
    ) -> T | None:
        ...

    @overload
    def get(
        self,
        option: str,
        typecast: Type[T],
        default: T,
        *,
        section: str | None = ...,
        recurse: Literal[False] = ...,
    ) -> T:
        ...

    @overload
    def get(
        self,
        option: str,
        typecast: Type[T],
        default: None = ...,
        *,
        section: str | None = ...,
        recurse: Literal[True],
    ) -> Sequence[T] | None:
        ...

    @overload
    def get(
        self,
        option: str,
        typecast: Type[T],
        default: T,
        *,
        section: str | None = ...,
        recurse: Literal[True],
    ) -> Sequence[T]:
        ...

    def get(
        self,
        option: str,
        typecast: Type[T],
        default: T | None = None,
        *,
        section: str | None = None,
        recurse: bool = False,
    ) -> Sequence[T] | T | None:
        value = self._getvalue(option, section=section, recurse=recurse)

        if isinstance(value, _NoValue):
            if recurse and default is not None:
                return (default,)
            return default

        if recurse:
            assert not isinstance(value, str)
            return tuple(self._resolve(v, typecast) for v in value)
        else:
            assert isinstance(value, str)
            return self._resolve(value, typecast)

    @overload
    def getlist(
        self,
        option: str,
        typecast: Type[T],
        default: None = ...,
        *,
        section: str | None = ...,
        recurse: Literal[False] = ...,
    ) -> Sequence[T] | None:
        ...

    @overload
    def getlist(
        self,
        option: str,
        typecast: Type[T],
        default: T,
        *,
        section: str | None = ...,
        recurse: Literal[False] = ...,
    ) -> Sequence[T]:
        ...

    @overload
    def getlist(
        self,
        option: str,
        typecast: Type[T],
        default: None = ...,
        *,
        section: str | None = ...,
        recurse: Literal[True],
    ) -> Sequence[Sequence[T]] | None:
        ...

    @overload
    def getlist(
        self,
        option: str,
        typecast: Type[T],
        default: T,
        *,
        section: str | None = ...,
        recurse: Literal[True],
    ) -> Sequence[Sequence[T]]:
        ...

    def getlist(
        self,
        option: str,
        typecast: Type[T],
        default: T | None = None,
        *,
        section: str | None = None,
        recurse: bool = False,
    ) -> Sequence[Sequence[T]] | Sequence[T] | None:
        value = self._getvalue(option, section=section, recurse=recurse)

        if isinstance(value, _NoValue):
            if default is None:
                return default
            elif recurse:
                return ((default,),)
            return (default,)

        if recurse:
            assert not isinstance(value, str)
            return tuple(
                tuple(
                    self._resolve(v, typecast)
                    for v in vlst.split(self._listsep)
                )
                for vlst in value
            )
        else:
            assert isinstance(value, str)
            return tuple(
                self._resolve(v, typecast) for v in value.split(self._listsep)
            )

    def _getvalue(
        self,
        option: str,
        *,
        section: str | None = None,
        recurse: bool = False,
    ) -> Sequence[str] | str | _NoValue:
        if not section and self.scope:
            option = f"{self.scope}.{option}"

        valuelist = list[str]() if recurse else None

        for _section in self.lookupchain(section=section):
            value = self._source.get(
                _section,
                option,
                vars=self.variables,
                fallback=_NoValue(),
            )
            if isinstance(value, _NoValue):
                continue
            elif recurse:
                assert isinstance(valuelist, list)
                valuelist.append(value)
                continue
            break
        else:
            value = _NoValue()

        if recurse:
            assert valuelist is not None
            return valuelist or _NoValue()
        else:
            return value

    def lookupchain(self, *, section: str | None = None) -> Iterable[str]:
        return (section,) if section else ()

    def _resolve(self, value: str, typecast: Type[T]) -> T:
        return caststrutil.resolve(value, typecast)
