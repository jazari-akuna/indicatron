"""
Exception classes for the Indicatron module.
"""


class IndicatronError(Exception):
    """Base exception for all Indicatron errors."""
    pass


class ConnectionError(IndicatronError):
    """Raised when a connection to the WLED device fails."""
    pass


class CommandError(IndicatronError):
    """Raised when a command to the WLED device fails."""
    pass
