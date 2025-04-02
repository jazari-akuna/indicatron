"""
Color definitions and conversions for WLED.
"""

# Predefined colors as RGB values
COLORS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
    "pink": (255, 192, 203),
    "teal": (0, 128, 128),
    "lime": (0, 255, 0),
    "brown": (165, 42, 42),
    "navy": (0, 0, 128),
    "olive": (128, 128, 0),
}


def parse_color(color):
    """
    Parse a color value from various formats into RGB tuple.
    
    Args:
        color (str or tuple): Either a color name, hex code, or RGB tuple
        
    Returns:
        tuple: RGB values as (r, g, b)
        
    Examples:
        >>> parse_color("red")
        (255, 0, 0)
        >>> parse_color("#FF0000")
        (255, 0, 0)
        >>> parse_color((255, 0, 0))
        (255, 0, 0)
    """
    if isinstance(color, tuple) and len(color) == 3:
        return color
    
    if isinstance(color, str):
        # Check if it's a predefined color name
        if color.lower() in COLORS:
            return COLORS[color.lower()]
        
        # Check if it's a hex color code
        if color.startswith('#') and len(color) in (4, 7):
            color = color.lstrip('#')
            if len(color) == 3:
                color = ''.join(c + c for c in color)
            return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    
    # If we get here, the color format is invalid
    raise ValueError(f"Invalid color format: {color}. Use color name, hex (e.g., #FF0000), or RGB tuple.")


def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color string."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
