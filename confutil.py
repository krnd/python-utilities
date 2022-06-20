from configparser import ConfigParser
from typing import Any, Final, Iterable, Mapping, Type

from arborister.utilities import filesearchutil, pathutil


try:
    from arborister.utilities.configparser.interpolation.brace import (
        BraceInterpolation as DefaultInterpolation,
    )
except ModuleNotFoundError:
    from configparser import BasicInterpolation as DefaultInterpolation


__version__ = "0.0.0"
__description__ = ""

__author__ = "Kilian Kaiping (krnd)"
__copyright__ = "Copyright (c) 2022 Kilian Kaiping (krnd)"
__license__ = "MIT"

__compatibility__ = "3.10"
__dependencies__ = ()
__utilities__ = ("filesearchutil", "pathutil")

__all__ = (
    # fmt:off
    "DEFAULT_ENCODING", "DEFAULT_SECTION", "DEFAULT_PARSERARGS",
    "create",
    "load", "searchload",
    # fmt:on
)


_EmptyMapping: Final = dict[Any, Any]()


DEFAULT_ENCODING: Final = "utf-8"

DEFAULT_SECTION: Final = "!@#$%^&*()_+"

# fmt:off
DEFAULT_PARSERARGS: Final = dict[str, Any](
    defaults=None,                         # None
    dict_type=dict,                        # dict
    allow_no_value=True,                   # False
    delimiters=("=",),                     # ("=", ":")
    comment_prefixes=("#", ";"),           # ("#", ";")
    inline_comment_prefixes=("#",),        # None
    strict=True,                           # True
    empty_lines_in_values=False,           # True
    default_section=DEFAULT_SECTION,       # configparser.DEFAULTSECT
    interpolation=DefaultInterpolation(),  # BasicInterpolation()
    converters=dict[str, Any](),           # dict()
)
# fmt:on


def create(
    *,
    parser_type: Type[ConfigParser] = ConfigParser,
    sourceattr: bool = True,
    parserargs: Mapping[str, Any] = DEFAULT_PARSERARGS,
    overwrites: Mapping[str, str] = _EmptyMapping,
    **overwrites_: str,
) -> ConfigParser:
    config = parser_type(**parserargs)
    if sourceattr:
        setattr(config, "source_path", None)

    config.read_dict({config.default_section: dict(overwrites) | overwrites_})

    return config


def load(
    filepath: str | None,
    *,
    basepath: str | None = None,
    encoding: str = DEFAULT_ENCODING,
    parser_type: Type[ConfigParser] = ConfigParser,
    sourceattr: bool = True,
    parserargs: Mapping[str, Any] = DEFAULT_PARSERARGS,
    overwrites: Mapping[str, str] = _EmptyMapping,
    **overwrites_: str,
) -> ConfigParser:
    config = parser_type(**parserargs)
    if sourceattr:
        setattr(config, "source_path", None)

    if filepath and pathutil.exists(filepath, basepath=basepath):
        filepath_ = pathutil.abspath(filepath, basepath=basepath)
        config.read(filepath_, encoding=encoding)
        if sourceattr:
            setattr(config, "source_path", filepath)

    config.read_dict({config.default_section: dict(overwrites) | overwrites_})

    return config


def searchload(
    paths: str | Iterable[str],
    filenames: str | Iterable[str],
    filetypes: str | Iterable[str],
    *,
    hidden: filesearchutil._SearchHiddenParameter = False,  # type: ignore
    basepath: str | None = None,
    parser_type: Type[ConfigParser] = ConfigParser,
    parserargs: Mapping[str, Any] = DEFAULT_PARSERARGS,
    overwrites: Mapping[str, str] = _EmptyMapping,
    **overwrites_: str,
) -> ConfigParser | None:
    search_paths = filesearchutil.get_paths(
        paths,
        filenames,
        filetypes,
        hidden=hidden,
        basepath=basepath or ".",
    )
    filepath = filesearchutil.find(search_paths)
    return load(
        filepath,
        basepath=basepath,
        parser_type=parser_type,
        parserargs=parserargs,
        overwrites=overwrites,
        **overwrites_,
    )
