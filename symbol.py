from typing import Any, ClassVar, Type
from typing_extensions import Self


__version__ = "0.0.0"
__description__ = ""

__author__ = "Kilian Kaiping (krnd)"
__copyright__ = "Copyright (c) 2022 Kilian Kaiping (krnd)"
__license__ = "MIT"

__compatibility__ = "3.10"
__dependencies__ = ("typing_extensions",)
__utilities__ = ()

__all__ = ("Symbol",)


class Symbol:

    __slots__ = ()

    name: ClassVar[str]
    value: ClassVar[Self]

    _bool: ClassVar[bool]

    def __init_subclass__(cls, *, bool: bool = True) -> None:
        cls.name = cls.__name__
        cls.value = cls()

        cls._bool = bool

        def __new__(cls: Type[Self]) -> Self:
            return cls.value

        cls.__new__ = __new__

    def __bool__(self) -> bool:
        return self._bool

    def __eq__(self, other: Any) -> bool:
        return other is self

    def __ne__(self, other: Any) -> bool:
        return other is not self

    def __hash__(self) -> int:
        return id(self)

    def __repr__(self) -> str:
        return f"<Symbol '{self.name}'>"

    def __str__(self) -> str:
        return self.name
