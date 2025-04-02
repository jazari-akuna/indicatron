"""
Indicatron: A Python module for controlling WLED-powered LED strips.
"""

__version__ = '0.1.0'

from .client import WLEDClient
from .colors import COLOR_MAP, WLED_EFFECTS

__all__ = ['WLEDClient', 'COLOR_MAP', 'WLED_EFFECTS']
