from __future__ import annotations

import functools
import sys
import time
from types import ModuleType, TracebackType
from typing import TYPE_CHECKING, Any, Callable

from ._types import Trace, TraceEntry

if TYPE_CHECKING:
    from typing_extensions import Self


class TracedModule:
    """
    Context manager for tracing module calls in Python.

    Methods
    -------
    __enter__
        Use to enter the context manager.
    __exit__
        Use to exit the context manager.
    get_trace
        Use to get the trace of the module calls.
    """

    def __init__(self: Self, name: str, callback: Callable[[str], None]) -> None:
        """
        Use to trace module calls.

        Parameters
        ----------
        name : str
            The name of the module to trace.
        callback : Callable[[str], None]
            The callback function to call when a module call is traced.
        """
        self._name: str = name
        self._callback: Callable[[str], None] = callback
        self._trace: Trace = []
        self._traced_module: ModuleType = TracedModule._get_traced_module(
            self._name,
            tracer_func=functools.partial(self._tracer_func, callback=self._callback),
        )
        self._original_module: ModuleType = sys.modules[self._name]

        # create a local trace list which gets intialized when the context manager is entered
        self._trace: Trace = []

    def __enter__(self: Self) -> None:
        self.begin()

    def __exit__(
        self: Self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.end()

    @staticmethod
    def _get_traced_module(
        name: str,
        tracer_func: Callable[[Callable], Callable],
        traced_modules: set[str] | None = None,
    ) -> ModuleType:
        if traced_modules is None:
            traced_modules = set()
        in_mod: ModuleType = sys.modules[name]
        for attr in dir(in_mod):
            if not attr.startswith("_"):
                func: Any = getattr(in_mod, attr)
                print(f"attr: {attr}, func: {func}, type: {type(func)}")
                print(f"{isinstance(func, ModuleType)}")
                # handle module level functions
                if callable(func):
                    setattr(in_mod, attr, tracer_func(func))
        return in_mod

    def _tracer_func(
        self: Self, func: Callable, callback: Callable[[str], None]
    ) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: tuple[Any], **kwargs: dict[str, Any]) -> Any:  # noqa: ANN401
            in_args, in_kwargs = args, kwargs
            result: Any = func(*args, **kwargs)
            self._trace = TraceEntry(
                time.monotonic(), self._name, func.__name__, in_args, in_kwargs
            )
            callback(f"{self._name}.{func.__name__}")
            return result

        return wrapper

    def begin(self: Self) -> None:
        """Use to begin tracing module calls."""
        sys.modules[self._name] = self._traced_module

    def end(self: Self) -> None:
        """Use to end tracing module calls."""
        sys.modules[self._name] = self._original_module

    def get_trace(self: Self) -> Trace:
        """
        Use to get the trace of the module calls.

        Returns
        -------
        Trace
            The trace of the module calls.
        """
        return self._trace