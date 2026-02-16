# config.py - Global Configuration

import os

# ADB - Nox emulator default port
ADB_HOST = "127.0.0.1"
ADB_PORT = 62001
NOX_ADB_PATH = r"D:\Program Files\Nox\bin\nox_adb.exe"

# Screenshot
SCREENSHOT_DIR = "data/screenshots"

# Resolution (detected from Nox emulator: portrait 1080x1920)
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 1920

# Claude API
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
LLM_MODEL = "claude-sonnet-4-20250514"
LLM_MAX_TOKENS = 1024

# Timing
LOOP_INTERVAL = 2.0          # seconds between main loop iterations
LLM_CONSULT_INTERVAL = 1800  # seconds between LLM strategic calls (~30min)

# Template matching
TEMPLATE_MATCH_THRESHOLD = 0.8

# Grid overlay
GRID_COLS = 8
GRID_ROWS = 6

# Paths
TEMPLATE_DIR = "templates"
STATE_FILE = "data/game_state.json"
TASKS_FILE = "data/tasks.json"
NAV_PATHS_FILE = "data/navigation_paths.json"

# Logging
LOG_DIR = "logs"
