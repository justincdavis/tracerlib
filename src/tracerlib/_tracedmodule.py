from __future__ import annotations

import functools
import importlib
import sys
import time
import warnings
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable

from ._stdlib import _stdlib
from ._types import Trace, TraceEntry

if TYPE_CHECKING:
    from types import TracebackType

    from typing_extensions import Self


class TracedModule:
    """
    Context manager for tracing module calls in Python.

    Methods
    -------
    __enter__
        Use to enter the context manager, calls begin.
    __exit__
        Use to exit the context manager, calls end.
    begin
        Use to begin tracing module calls.
    end
        Use to end tracing module calls.
    get_trace
        Use to get the trace of the module calls.
    """

    def __init__(
        self: Self,
        name: str,
        callback: Callable[[str], None],
        trace_submodules: bool | None = None,
    ) -> None:
        """
        Use to trace module calls.

        Parameters
        ----------
        name : str
            The name of the module to trace.
        callback : Callable[[str], None]
            The callback function to call when a module call is traced.
        trace_submodules : bool, optional
            Whether to trace the submodules of the module, by default None
            If None, then the submodules are traced.
        """
        self._name: str = name
        self._callback: Callable[[str], None] = callback
        if trace_submodules is None:
            trace_submodules = False
        self._trace_submodules: bool = trace_submodules

        # variable declarations
        self._traced_module: ModuleType | None = None
        self._original_module: ModuleType | None = None
        self._original_submodules: set[ModuleType] | None = None
        self._traced_submodules: set[ModuleType] | None = None

        # create a local trace list which gets intialized when the context manager is entered
        self._trace: Trace = []

    def __enter__(self: Self) -> Self:
        self.begin()
        return self

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
        traced_functions: set[str] | None = None,
        traced_modules: set[str] | None = None,
    ) -> ModuleType:
        if traced_functions is None:
            traced_functions = set()
        if traced_modules is None:
            traced_modules = set()
        traced_modules.add(name)
        in_mod: ModuleType = sys.modules[name]
        for attr in dir(in_mod):
            if not attr.startswith("_"):
                func: Any = getattr(in_mod, attr)
                if callable(func) and attr not in traced_functions:
                    traced_functions.add(attr)
                    setattr(in_mod, attr, tracer_func(func))
        return in_mod

    @staticmethod
    def _get_submodules(
        module: ModuleType, exclude: set[str] | None = None
    ) -> set[ModuleType]:
        if exclude is None:
            exclude = set()
        submodules = set()
        for attr in dir(module):
            if not attr.startswith("_"):
                thing = getattr(module, attr)
                if (
                    isinstance(thing, ModuleType)
                    and thing not in exclude
                    and attr not in _stdlib
                ):
                    submodules.add(thing)
                    exclude.add(attr)
                    # submodule_submodules = TracedModule._get_submodules(
                    #     thing, exclude=exclude
                    # )
                    # submodules.update(submodule_submodules)
        return submodules

    def _tracer_func(
        self: Self,
        func: Callable,
        callback: Callable[[str], None],
        submodule: str | None = None,
    ) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: tuple[Any], **kwargs: dict[str, Any]) -> Any:  # noqa: ANN401
            in_args, in_kwargs = args, kwargs
            result: Any = func(*args, **kwargs)
            self._trace.append(
                TraceEntry(
                    time.monotonic(), self._name, func.__name__, in_args, in_kwargs
                )
            )
            mod_name = self._name if submodule is None else submodule
            callback(f"{mod_name}.{func.__name__}")
            return result

        return wrapper

    def begin(self: Self) -> None:
        """Use to begin tracing module calls."""
        traced_mod = TracedModule._get_traced_module(
            self._name,
            tracer_func=functools.partial(self._tracer_func, callback=self._callback),
        )
        self._traced_module = traced_mod
        self._original_submodules = TracedModule._get_submodules(self._traced_module)
        self._traced_submodules = set()
        if self._trace_submodules:
            for submodule in self._original_submodules:
                traced_submod = TracedModule._get_traced_module(
                    submodule.__name__,
                    tracer_func=functools.partial(
                        self._tracer_func,
                        callback=self._callback,
                        submodule=submodule.__name__,
                    ),
                )
                self._traced_submodules.add(traced_submod)
        self._original_module = sys.modules[self._name]
        sys.modules[self._name] = self._traced_module
        if self._trace_submodules:
            for submodule in self._traced_submodules:
                sys.modules[submodule.__name__] = submodule

    def end(self: Self) -> None:
        """
        Use to end tracing module calls.

        Raises
        ------
        RuntimeError
            If the tracing has not been started.
        """
        if self._original_module is None or self._original_submodules is None:
            raise RuntimeError("Cannot end tracing before beginning tracing.")
        sys.modules[self._name] = self._original_module
        if self._trace_submodules:
            for submodule in self._original_submodules:
                sys.modules[submodule.__name__] = submodule
        warnings.filterwarnings("ignore")
        with warnings.catch_warnings():
            importlib.reload(sys.modules[self._name])
        warnings.filterwarnings("default")

    def get_trace(self: Self) -> Trace:
        """
        Use to get the trace of the module calls.

        Returns
        -------
        Trace
            The trace of the module calls.
        """
        return self._trace
