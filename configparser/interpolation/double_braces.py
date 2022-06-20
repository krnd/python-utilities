# pyright: reportMissingParameterType=false
# pyright: reportMissingTypeArgument=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownVariableType=false

import re
from configparser import (
    ConfigParser,
    Interpolation,
    InterpolationDepthError,
    InterpolationMissingOptionError,
    InterpolationSyntaxError,
)
from typing import Mapping


# flake8: noqa
# fmt:off


class DoubleBracesInterpolation(Interpolation):
    """Interpolation as implemented in the classic ConfigParser.

    The option values can contain format strings which refer to other values in
    the same section, or values in the special default section.

    For example:

        something: {{dir}}/whatever

    would resolve the "{{dir}}" to the value of dir.  All reference
    expansions are done late, on demand. If a user needs to use a bare {{/}} in
    a configuration file, she can escape it by writing {{{/}}}. Other {{/}} usage
    is considered a user error and raises `InterpolationSyntaxError'."""


    _KEYCRE = re.compile(r"\{\{((?:[^\}]+|\}(?!\})|\}(?=\}\}))+)\}\}")                              # cspell:ignore KEYCRE


    def before_get(self, parser, section, option, value, defaults):
        L = []
        self._interpolate_some(parser, option, L, value, section, defaults, 1)
        return ''.join(L)

    def before_set(self, parser, section, option, value):
        tmp_value = value.replace('{{{', '').replace('}}}', '')  # escape braces
        tmp_value = self._KEYCRE.sub('', tmp_value)  # valid syntax
        if '{{' in tmp_value:
            raise ValueError("invalid interpolation syntax in %r at "
                             "position %d" % (value, tmp_value.find('{{')))
        elif '}}' in tmp_value:
            raise ValueError("invalid interpolation syntax in %r at "
                             "position %d" % (value, tmp_value.find('}}')))
        return value


    def _interpolate_some(self, parser, option, accum, rest, section, map,                          # cspell:ignore accum
                          depth):
        rawval = parser.get(section, option, raw=True, fallback=rest)
        if depth > 1:  # MAX_INTERPOLATION_DEPTH
            raise InterpolationDepthError(option, section, rawval)
        while rest:
            p = rest.find("{{")
            if p < 0:
                accum.append(rest)
                return
            if p > 0:
                accum.append(rest[:p])
                rest = rest[p:]
            # p is no longer used
            c = rest[2:3]
            if c == "{":
                accum.append("{{")
                rest = rest[3:]
            else:
                m = self._KEYCRE.match(rest)
                if m is None:
                    raise InterpolationSyntaxError(option, section,
                            "bad interpolation variable reference %r" % rest)
                var = parser.optionxform(m.group(1))                                                # cspell:ignore optionxform
                rest = rest[m.end():]
                try:
                    v = self._resolve(parser, option, section, map, var)
                except KeyError:
                    raise InterpolationMissingOptionError(
                            option, section, rawval, var) from None
                if "{{" in v:
                    self._interpolate_some(parser, option, accum, v,
                                           section, map, depth + 1)
                else:
                    accum.append(v)


    def _resolve(self, parser: ConfigParser, option: str, section: str, map: Mapping, var: str):
        return map[var]
