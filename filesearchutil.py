import itertools
import typing
from typing import Callable, Iterable, Literal, Sequence, Tuple, TypeAlias

from arborister.utilities import pathutil


__version__ = "0.0.0"
__description__ = ""

__author__ = "Kilian Kaiping (krnd)"
__copyright__ = "Copyright (c) 2022 Kilian Kaiping (krnd)"
__license__ = "MIT"

__compatibility__ = "3.10"
__dependencies__ = ()
__utilities__ = ("pathutil",)

__all__ = (
    # fmt:off
    'get_paths',
    'find', 'findall',
    'glob', 'globall',
    # fmt:on
)


_SearchHidden: TypeAlias = typing.Union[bool, Literal["only"]]
_SearchHiddenParameter: TypeAlias = typing.Union[
    _SearchHidden,
    Tuple[_SearchHidden],
    Tuple[_SearchHidden, _SearchHidden],
]


def get_paths(
    paths: str | Iterable[str],
    filenames: str | Iterable[str],
    filetypes: str | Iterable[str],
    *,
    hidden: _SearchHiddenParameter = False,
    pathify: Callable[..., str] = pathutil.abspath,
    basepath: str | None = None,
) -> Iterable[str]:
    paths = tuple(paths) if isinstance(paths, str) else paths
    filenames = tuple(filenames) if isinstance(filenames, str) else filenames
    filetypes = tuple(filetypes) if isinstance(filetypes, str) else filetypes

    if not isinstance(hidden, tuple):
        hidden_paths, hidden_files = hidden, hidden
    elif len(hidden) == 1:
        hidden_paths, hidden_files = False, *hidden
    else:
        hidden_paths, hidden_files = hidden
    paths = _apply_hidden_parameter(paths, hidden_paths)
    filenames = _apply_hidden_parameter(filenames, hidden_files)

    search_paths = list[str]()
    # cspell:ignore fpath, fname, fext
    for fpath, fname, fext in itertools.product(paths, filenames, filetypes):
        fext = f".{fext}" if fext else ""
        fullpath = pathify(fpath, fname + fext, basepath=basepath)
        search_paths.append(fullpath)
    return search_paths


def _apply_hidden_parameter(
    entries: Iterable[str],
    hidden: _SearchHidden,
) -> Iterable[str]:
    normal_entries = (pathutil.normpath(entry) for entry in entries)
    if not hidden:
        return normal_entries
    hidden_entries = (pathutil.hidden(entry) for entry in entries)
    if hidden == "only":
        return hidden_entries
    return itertools.chain.from_iterable(zip(normal_entries, hidden_entries))


def _findsearch(
    paths: Iterable[str],
    basepath: str | None,
    pathify: Callable[..., str],
    firstmatch: bool,
) -> str | Iterable[str] | None:
    allfiles = list[str]()
    for filepath in paths:
        filepath = pathify(filepath, basepath=basepath)
        if pathutil.isfile(filepath):
            if firstmatch:
                return filepath
            allfiles.append(filepath)
    return None if firstmatch else allfiles


def find(
    paths: Iterable[str],
    *,
    pathify: Callable[..., str] = pathutil.abspath,
    basepath: str | None = None,
) -> str | None:
    file = _findsearch(paths, basepath, pathify, firstmatch=True)
    assert file is None or isinstance(file, str)
    return file


def findall(
    paths: Iterable[str],
    *,
    pathify: Callable[..., str] = pathutil.abspath,
    basepath: str | None = None,
) -> Iterable[str]:
    files = _findsearch(paths, basepath, pathify, firstmatch=False)
    assert files is not None and not isinstance(files, str)
    return files


def _globsearch(
    paths: Iterable[str],
    globify: Callable[..., Sequence[str]],
    basepath: str | None,
    firstmatch: bool,
) -> str | Iterable[str] | None:
    allfiles = list[str]()
    for globpath in paths:
        filepaths = globify(globpath, basepath=basepath)
        if filepaths:
            if firstmatch:
                return filepaths[0]
            allfiles.extend(filepaths)
    return None if firstmatch else allfiles


def glob(
    paths: str | Iterable[str],
    *,
    globify: Callable[..., Sequence[str]] = pathutil.absglob,
    basepath: str | None = None,
) -> str | None:
    if isinstance(paths, str):
        paths = (paths,)
    file = _globsearch(paths, globify, basepath, firstmatch=True)
    assert file is None or isinstance(file, str)
    return file


def globall(
    paths: str | Iterable[str],
    *,
    globify: Callable[..., Sequence[str]] = pathutil.absglob,
    basepath: str | None = None,
) -> Iterable[str]:
    if isinstance(paths, str):
        paths = (paths,)
    files = _globsearch(paths, globify, basepath, firstmatch=False)
    assert files is not None and not isinstance(files, str)
    return files
