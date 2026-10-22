"""Strict, dependency-free audit of precomputed SCONE/OpenSim STO tables."""

from .analysis import STOError, analyze, read_sto

__version__ = "0.2.0"
__all__ = ["STOError", "analyze", "read_sto", "__version__"]
