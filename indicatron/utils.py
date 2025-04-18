"""
Utility functions for the Indicatron module.
"""
from .colors import COLOR_MAP
from .exceptions import WLEDValueError

def resolve_color(color):
    """
    Resolve a color string or tuple to an RGB tuple.
    
    Args:
        color: Color name (string) or RGB tuple
        
    Returns:
        RGB tuple
        
    Raises:
        WLEDValueError: If the color is invalid
    """
    if isinstance(color, (list, tuple)):
        if len(color) == 3 and all(isinstance(v, int) and 0 <= v <= 255 for v in color):
            return list(color)  # Convert to list for JSON serialization
        raise WLEDValueError(f"Invalid RGB color: {color}")
    
    if isinstance(color, str):
        color = color.lower()
        if color in COLOR_MAP:
            return list(COLOR_MAP[color])  # Convert to list for JSON serialization
        raise WLEDValueError(f"Unknown color name: {color}")
    
    raise WLEDValueError(f"Invalid color type: {type(color)}")

def validate_brightness(brightness):
    """
    Validate and normalize brightness value.
    
    Args:
        brightness: Brightness value between 0 and 255 or 0 and 100%
        
    Returns:
        Normalized brightness value between 0 and 255
        
    Raises:
        WLEDValueError: If the brightness is invalid
    """
    if isinstance(brightness, str) and brightness.endswith('%'):
        try:
            percentage = float(brightness[:-1])
            if 0 <= percentage <= 100:
                return int(percentage * 255 / 100)
            raise WLEDValueError(f"Brightness percentage must be between 0 and 100: {brightness}")
        except ValueError:
            raise WLEDValueError(f"Invalid brightness percentage: {brightness}")
    
    try:
        brightness = int(brightness)
        if 0 <= brightness <= 255:
            return brightness
        raise WLEDValueError(f"Brightness must be between 0 and 255: {brightness}")
    except ValueError:
        raise WLEDValueError(f"Invalid brightness value: {brightness}")
