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
    with tracerlib.TracedModule("numpy", print):
        with tracerlib.TracedModule("numpy.linalg", print):
            # create some matrices and then multiply them
            print("line 0")
            a = np.array([[1, 0], [0, 1]])
            print("line 1")
            b = np.array([[4, 1], [2, 2]])
            print("line 2")
            c = a + b
            print("line 3")
            c = np.linalg.inv(c)
            print("line 4")
            np.transpose(c)
            print("line 5")

if __name__ == "__main__":
    main()
