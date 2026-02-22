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

# LLM Configuration - loaded from model_presets.py
from model_presets import get_active_preset as _get_preset
_preset = _get_preset()
LLM_PROVIDER = _preset["provider"]           # "anthropic" or "openai_compatible"
LLM_BASE_URL = _preset["base_url"]           # API endpoint
LLM_API_KEY = _preset["api_key"]             # API key
LLM_MODEL = _preset["model_name"]            # Text model
LLM_VISION_MODEL = _preset["vision_model"]   # Vision model (for screenshots)
LLM_MAX_TOKENS = _preset["max_tokens"]

# Backward compat
ANTHROPIC_API_KEY = LLM_API_KEY if LLM_PROVIDER == "anthropic" else ""

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

# Multi-game support
GAMES_DIR = "games"
ACTIVE_GAME = "westgame2"

# Logging
LOG_DIR = "logs"

# Phase 5: Hardening
GAME_PACKAGE = "leyi.cowboyclash3"  # Android package name (for app restart recovery)
STUCK_MAX_SAME_SCENE = 10       # Trigger stuck recovery after N identical scenes
ADB_RECONNECT_RETRIES = 3       # Max ADB reconnection attempts
ACTION_MAX_RETRIES = 3           # Max retries per failed action
