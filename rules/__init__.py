"""rules — detector engine and detectors (S2)."""

from .detectors import DETECTORS, Detector
from .engine import run_detectors

__all__ = ["DETECTORS", "Detector", "run_detectors"]
