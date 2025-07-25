"""
config.py

This module centralizes configuration constants for the TI-84 Graphing Calculator.
It includes color schemes, fonts, graphing parameters, and default settings for the calculator engine.
"""

# ---------------------------
# Color and Theme Settings
# ---------------------------
# UI Colors
BG_COLOR = "#000000"         # Background for graph display (black)
DISPLAY_BG = "#000000"       # Background for the expression display (black)
DISPLAY_FG = "#00FF00"       # Display text color (classic green)
BTN_BG = "#333333"           # Button background color (dark gray)
BTN_FG = "#FFFFFF"           # Button text color (white)

# ---------------------------
# Font Settings
# ---------------------------
FONT_DISPLAY = ("Courier", 20)   # Font for the expression display
FONT_BTN = ("Courier", 14)       # Font for the keypad buttons

# ---------------------------
# Graphing Parameters
# ---------------------------
GRAPH_X_RANGE = (-10, 10)        # Default x-axis range for graphing
GRAPH_Y_RANGE = (-10, 10)        # Default y-axis range for graphing
GRID_SPACING = 20                # Pixel spacing between grid lines
GRID_COLOR = "#444444"           # Color for grid lines
FUNCTION_COLOR = "#00FF00"       # Color for plotted functions (matching display text)

# ---------------------------
# Calculator Engine Defaults
# ---------------------------
DEFAULT_ANGLE_MODE = "RAD"       # Default angle mode for trigonometric functions
