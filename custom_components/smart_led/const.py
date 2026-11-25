"""Constants for the Smart LED integration."""

DOMAIN = "smart_led"

CONF_FRAME_SERVICE = "frame_service"

WIDTH = 12
HEIGHT = 10

# Each line is 5 rows high: top uses rows 0-4, bottom rows 5-9.
LINE_ROWS = {"top": 0, "bottom": 5}

# Three 3-pixel slots per line with a 1-pixel gap: left, separator, right.
SLOT_COLUMNS = {"left": 0, "separator": 4, "right": 8}

ATTR_DISPLAY = "display"
ATTR_LINE = "line"
ATTR_COLOR = "color"
