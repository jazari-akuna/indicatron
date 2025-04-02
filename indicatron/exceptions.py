"""
Exception classes for WLED client.
"""

class WLEDError(Exception):
    """Base class for WLED-related errors."""
    pass

class WLEDConnectionError(WLEDError):
    """Error connecting to WLED device."""
    pass

class WLEDResponseError(WLEDError):
    """Error in response from WLED device."""
    pass

class WLEDValueError(WLEDError):
    """Invalid value provided for WLED command."""
    pass
