import glob
import os
import os.path
from typing import Iterable, Sequence


__version__ = "0.0.0"
__description__ = ""

__author__ = "Kilian Kaiping (krnd)"
__copyright__ = "Copyright (c) 2022 Kilian Kaiping (krnd)"
__license__ = "MIT"

__compatibility__ = "3.10"
__dependencies__ = ()
__utilities__ = ()

__all__ = (
    # fmt:off
    "join",
    "normpath", "abspath", "realpath", "relpath",
    "exists", "isfile", "isdir",
    "isabs", "isreal", "islink",
    "dirname", "basename", "filename", "fileext",
    "startswith", "endswith",
    "replace",
    "hidden",
    "normglob", "absglob", "realglob", "relglob",
    # fmt:on
)


def _path(
    paths: Iterable[str],
    basepath: str | None,
) -> str:
    path = paths if isinstance(paths, str) else os.path.join(*paths)
    if basepath and not os.path.isabs(path):
        path = os.path.join(basepath, path)
    return path.rstrip(os.sep)


def join(
    *paths: str,
    basepath: str | None = None,
) -> str:
    return _path(paths, basepath)


def normpath(
    *paths: str,
    basepath: str | None = None,
) -> str:
    fullpath = _path(paths, basepath)
    return os.path.normpath(fullpath)


def abspath(
    *paths: str,
    basepath: str | None = None,
    realdir: bool = False,
) -> str:
    fullpath = _path(paths, basepath)
    if realdir:
        dirname, basename = os.path.split(fullpath)
        return os.path.join(os.path.realpath(dirname), basename)
    else:
        return os.path.abspath(fullpath)


def realpath(
    *paths: str,
    basepath: str | None = None,
    realbase: bool = False,
) -> str:
    fullpath = _path(paths, basepath)
    if realbase:
        return os.path.realpath(fullpath)
    else:
        dirname, basename = os.path.split(fullpath)
        return os.path.join(os.path.realpath(dirname), basename)


def relpath(
    *paths_and_start: str,
    realbase: bool = False,
) -> str:
    *paths, start = paths_and_start
    fullpath = realpath(*paths, realbase=realbase)
    start = os.path.realpath(start)
    return os.path.relpath(fullpath, start)


def exists(
    *paths: str,
    basepath: str | None = None,
) -> bool:
    fullpath = _path(paths, basepath=basepath)
    return os.path.exists(fullpath)


def isfile(
    *paths: str,
    basepath: str | None = None,
) -> bool:
    fullpath = _path(paths, basepath=basepath)
    return os.path.isfile(fullpath)


def isdir(
    *paths: str,
    basepath: str | None = None,
) -> bool:
    fullpath = _path(paths, basepath=basepath)
    return os.path.isdir(fullpath)


def isabs(
    *paths: str,
    basepath: str | None = None,
) -> bool:
    fullpath = _path(paths, basepath=basepath)
    return os.path.isabs(fullpath)


def isreal(  # cspell:ignore isreal
    *paths: str,
    basepath: str | None = None,
) -> bool:
    fullpath = _path(paths, basepath=basepath)
    if not os.path.isabs(fullpath):
        return False
    return fullpath == os.path.realpath(fullpath)


def islink(
    *paths: str,
    basepath: str | None = None,
) -> bool:
    fullpath = _path(paths, basepath=basepath)
    return os.path.islink(fullpath)


def dirname(*paths: str) -> str:
    fullpath = normpath(*paths)
    return os.path.dirname(fullpath)


def basename(*paths: str) -> str:
    fullpath = normpath(*paths)
    return os.path.basename(fullpath)


def filename(*paths: str) -> str:
    fullpath = normpath(*paths)
    return os.path.splitext(os.path.basename(fullpath))[0]


def fileext(*paths: str) -> str:
    fullpath = normpath(*paths)
    return os.path.splitext(os.path.basename(fullpath))[-1]


def startswith(
    *paths: str,
    prefix: str,
) -> bool:
    pathitems = abspath(*paths).split(os.sep)
    return any(item.startswith(prefix) for item in pathitems)


def endswith(
    *paths: str,
    prefix: str,
) -> bool:
    pathitems = abspath(*paths).split(os.sep)
    return any(path_.endswith(prefix) for path_ in pathitems)


def replace(
    *paths: str,
    drive: str | None = None,
    subpath: str | None = None,
    dirname: str | None = None,
    basename: str | None = None,
    filename: str | None = None,
    fileext: str | None = None,
) -> str:
    fullpath = normpath(*paths)

    drive_, subpath_ = os.path.splitdrive(fullpath)
    drive_ = drive if drive is not None else drive_
    subpath_ = subpath if subpath is not None else subpath_

    if (
        dirname is not None
        or basename is not None
        or filename is not None
        or fileext is not None
    ):
        dirname_, basename_ = os.path.split(subpath_)
        dirname_ = dirname if dirname is not None else dirname_
        basename_ = basename if basename is not None else basename_

        if filename is not None or fileext is not None:
            filename_, fileext_ = os.path.splitext(basename_)
            filename_ = filename if filename is not None else filename_
            fileext_ = fileext if fileext is not None else fileext_

            return os.path.join(drive_, dirname_, filename_, fileext_)
        return os.path.join(drive_, dirname_, basename_)
    return os.path.join(drive_, subpath_)


def hidden(*paths: str):
    dirname, basename = os.path.split(normpath(*paths))
    return os.path.join(dirname, "." + basename)


def _glob(
    paths: Iterable[str],
    basepath: str | None,
    recursive: bool,
) -> Sequence[str]:
    fullpath = normpath(*paths, basepath=basepath)
    return glob.glob(fullpath, recursive=recursive)


def normglob(
    *paths: str,
    basepath: str | None = None,
    recursive: bool = False,
) -> Sequence[str]:
    globpaths = _glob(paths, basepath, recursive)
    return [os.path.normpath(path) for path in globpaths]


def absglob(
    *paths: str,
    basepath: str | None = None,
    recursive: bool = False,
) -> Sequence[str]:
    globpaths = _glob(paths, basepath, recursive)
    return [os.path.abspath(path) for path in globpaths]


def realglob(
    *paths: str,
    basepath: str | None = None,
    recursive: bool = False,
) -> Sequence[str]:
    globpaths = _glob(paths, basepath, recursive)
    return [os.path.realpath(path) for path in globpaths]


def relglob(
    *paths_and_start: str,
    basepath: str | None = None,
    recursive: bool = False,
) -> Sequence[str]:
    *paths, start = paths_and_start
    globpaths = _glob(paths, basepath, recursive)
    return [os.path.relpath(path, start) for path in globpaths]
