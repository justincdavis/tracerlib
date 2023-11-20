from __future__ import annotations

import os
import sys
import time
from typing import Any, Callable

import torch


_GLOBAL_STATE: list[tuple[float, str, tuple[tuple[Any, ...], dict[str, Any]], Any]] = []


def get_traced_module(name: str, tracer_func: Callable[[Callable], Callable]) -> Any:
    in_mod = sys.modules[name]
    for attr in dir(in_mod):
        if not attr.startswith("_"):
            func = getattr(in_mod, attr)
            if callable(func):
                setattr(in_mod, attr, tracer_func(func))
    return in_mod


# make a decorate which takes a function and prints the string provided and then prints when function decorated is called
def tracer(name: str):
    def tracer_func(func):
        def wrapper(*args, **kwargs):
            print(f"Calling {name}.{func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    # replace module with a version which prints whenever a function is called
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            global _GLOBAL_STATE
            funcname = func.__name__
            in_args = args
            in_kwargs = kwargs
            og_mod = sys.modules[name]
            traced_mod = get_traced_module(name)
            sys.modules[name] = traced_mod
            result = func(*args, **kwargs)
            sys.modules[name] = og_mod
            _GLOBAL_STATE.append((time.time(), funcname, (in_args, in_kwargs), result))
            return result
        return wrapper
    return decorator

@tracer("torch")
def test(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    return torch.add(a, b)

def main():    
    # create a function to trace input and outputs
    def tracer(func):
        def wrapper(*args, **kwargs):
            global _GLOBAL_STATE
            funcname = func.__name__
            in_args = args
            in_kwargs = kwargs
            result = func(*args, **kwargs)
            _GLOBAL_STATE.append((time.time(), funcname, (in_args, in_kwargs), result))
            return result
        return wrapper
    
    test(torch.Tensor(1), torch.Tensor(2))

    print("BREAK")
    # ensure no prints present for normal torch add
    r = torch.Tensor(1) + torch.Tensor(2)
    print(r)
    print("BREAK")

    global _GLOBAL_STATE
    print(_GLOBAL_STATE)

if __name__ == "__main__":
    main()
