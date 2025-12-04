#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration file for the Electric Vehicle Route Planning application.
Copy this file to config.py and modify as needed.
"""

# ======================= #
# ALGORITHM SETTINGS
# ======================= #

# Timeout for route search algorithms (seconds)
TIMEOUT_SECONDS = 600

# Average vehicle speed (km/h) - used for time calculations
AVG_SPEED_KMH = 60

# Road factor - multiplier to convert straight-line distance to road distance
# 1.25 means roads are approximately 25% longer than straight-line distance
ROAD_FACTOR = 1.25

# Earth radius in kilometers (for Haversine calculations)
R_EARTH = 6371.0


# ======================= #
# BOT (TOLL STATION) SETTINGS
# ======================= #

# Distance threshold (km) - routes within this distance from a BOT station
# are considered to pass through that station
BOT_PROXIMITY_THRESHOLD = 5.0


# ======================= #
# CHARGING SETTINGS
# ======================= #

# Charging rate (km/minute) - how fast the battery charges
# Default: 2 km per minute
CHARGING_RATE_KM_PER_MIN = 2.0

# Maximum charging percentage before charging becomes expensive
# Charging from 0-80% is often free or cheap, 80-100% is expensive
FREE_CHARGING_THRESHOLD = 80

# Charging costs (VND per minute)
CHARGING_COST_0_30_MIN = 1000   # First 30 minutes
CHARGING_COST_30_60_MIN = 2000  # 30-60 minutes
CHARGING_COST_60_PLUS_MIN = 3000  # Beyond 60 minutes


# ======================= #
# DATA FILES
# ======================= #

# Path to charging stations CSV file
CHARGING_STATIONS_FILE = 'charging_stations.csv'

# Path to BOT (toll) stations CSV file
BOT_STATIONS_FILE = 'BOT.csv'

# Output directory for PDF route exports
ROUTES_OUTPUT_DIR = 'routes'

# Font file for PDF exports (must support Unicode for Vietnamese)
PDF_FONT_FILE = 'Arial.ttf'


# ======================= #
# UI SETTINGS
# ======================= #

# Default theme (True = Dark Mode, False = Light Mode)
DEFAULT_DARK_MODE = True

# Default window size
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Dark mode colors
DARK_THEME = {
    "bg": "#2e2e2e",
    "fg": "white",
    "frame_bg": "#3c3c3c",
    "frame_fg": "#cccccc",
    "entry_bg": "#1e1e1e",
    "entry_fg": "#ffffff",
    "text_bg": "#1e1e1e",
    "text_fg": "#ffffff"
}

# Light mode colors
LIGHT_THEME = {
    "bg": "SystemButtonFace",
    "fg": "black",
    "frame_bg": "white",
    "frame_fg": "black",
    "entry_bg": "white",
    "entry_fg": "black",
    "text_bg": "white",
    "text_fg": "black"
}


# ======================= #
# OPTIMIZATION SETTINGS
# ======================= #

# Number of nearest charging stations to consider at each step
# Higher = more thorough search but slower
# Lower = faster search but may miss optimal routes
MAX_CANDIDATES_PER_STEP = 10


# ======================= #
# GEOCODING SETTINGS
# ======================= #

# User agent for geocoding requests (required by geopy)
GEOCODING_USER_AGENT = "ev_route_app"

# Timeout for geocoding requests (seconds)
GEOCODING_TIMEOUT = 5


# ======================= #
# LOGGING SETTINGS
# ======================= #

# Enable debug logging
DEBUG = False

# Log file path (None = no file logging)
LOG_FILE = None  # Example: 'ev_routing.log'


# ======================= #
# NOTES
# ======================= #

"""
To use this configuration file:

1. Copy this file to config.py:
   cp config.example.py config.py

2. Modify config.py with your settings

3. Import in your code:
   from config import TIMEOUT_SECONDS, AVG_SPEED_KMH, ...

4. Add config.py to .gitignore to avoid committing personal settings

Note: The application will use default values if config.py is not found.
"""
