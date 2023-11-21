"""
A basic example showcasing the use of the tracerlib module.

This example showcases the use of the tracerlib module by 
tracing the calls to the numpy module.
"""
from __future__ import annotations

import tracerlib

import numpy as np


def main():    
    with tracerlib.TracedModule("numpy", print):
        # create some matrices and then multiply them
        a = np.array([[1, 0], [0, 1]])
        b = np.array([[4, 1], [2, 2]])  
        c = a @ b
        c = np.linalg.inv(c)
        d = np.transpose(c)

if __name__ == "__main__":
    main()
