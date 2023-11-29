# ruff: disable
"""
A basic example showcasing the use of the tracerlib module.

This example showcases the use of the tracerlib module by
tracing the calls to the numpy module.
"""
from __future__ import annotations

import numpy as np
import tracerlib


def main():
    with tracerlib.TracedModule("numpy", print, trace_submodules=True) as tm:
        # create some matrices and then multiply them
        a = np.array([[1, 0], [0, 1]])
        b = np.array([[4, 1], [2, 2]])
        c = a + b
        c = np.linalg.inv(c)
        c= np.transpose(c)

        trace = tm.get_trace()  # important to not access the trace before exiting the context manager

    print("Trace:")
    for t in trace:
        print(t)

    _ = np.array([[1, 0], [0, 1]])  # no trace or callback present

if __name__ == "__main__":
    main()
