"""
Exceptions for the Indicatron module.
"""

class WLEDError(Exception):
    """Base exception for WLED errors."""
    pass

class WLEDConnectionError(WLEDError):
    """Error connecting to a WLED device."""
    pass

class WLEDResponseError(WLEDError):
    """Error in the response from a WLED device."""
    pass

class WLEDValueError(WLEDError):
    """Error in a value passed to a WLED function."""
    pass
