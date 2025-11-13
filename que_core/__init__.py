"""
que_core package — top-level bootstrap
This package provides the Python-side orchestration for the Que Core runtime.
It loads the Rust engine (que_core_engine) when available.
"""
# Lazy import for Rust extension (if built)
try:
    from . import _version  # placeholder for package version
except Exception:
    pass

# TODO: Provide high-level helpers to start runtime & server
__all__ = ["runtime", "api", "tools", "context", "plugins"]
