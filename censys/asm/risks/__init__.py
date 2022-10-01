"""Interact with the Censys Risks API."""
from .v1 import Risksv1
from .v2 import Risksv2

Risks = Risksv2

__all__ = ["Risks", "Risksv1", "Risksv2"]
