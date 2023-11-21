from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from typing_extensions import Self, TypeAlias


@dataclass(init=True, eq=True, repr=False)
class TraceEntry:
    timestamp: float
    module_name: str
    func_name: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]

    def __init__(
        self: Self,
        timestamp: float,
        module_name: str,
        func_name: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> None:
        self.timestamp = timestamp
        self.module_name = module_name
        self.func_name = func_name
        self.args = args
        self.kwargs = kwargs

    def __repr__(self: Self) -> str:
        return f"TraceEntry(timestamp={self.timestamp}, module_name={self.module_name}, func_name={self.func_name}, args={self.args}, kwargs={self.kwargs})"

    def __str__(self: Self) -> str:
        return f"TraceEntry(timestamp={self.timestamp}, module_name={self.module_name}, func_name={self.func_name}, args={self.args}, kwargs={self.kwargs})"


Trace: TypeAlias = "list[TraceEntry]"
