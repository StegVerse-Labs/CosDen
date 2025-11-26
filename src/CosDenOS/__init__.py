"""
CosDenOS Python package initializer.
This file allows imports like:

    import CosDenOS
    from CosDenOS.api import cosden_router

and ensures the package is recognized during validation.
"""

# Optional: expose commonly used components
try:
    from .api import cosden_router  # if api.py exists
except Exception:
    pass
