from __future__ import annotations

from stdlib_list import stdlib_list


def _get_stdlib_modules() -> list[str]:
    return stdlib_list()


_stdlib = _get_stdlib_modules()
