# config.py - Global Configuration

import os
import shutil


def _find_nox_adb() -> str:
    """Auto-detect nox_adb.exe from common install locations and registry."""
    # Common candidate paths across C/D drives
    candidates = [
        r"D:\Program Files\Nox\bin\nox_adb.exe",
        r"C:\Program Files\Nox\bin\nox_adb.exe",
        r"D:\Program Files (x86)\Nox\bin\nox_adb.exe",
        r"C:\Program Files (x86)\Nox\bin\nox_adb.exe",
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path

    # Fallback: check Windows registry for Nox install path
    try:
        import winreg
        for reg_path in [
            r"SOFTWARE\BigNox\VirtualBox Guest Additions",
            r"SOFTWARE\WOW6432Node\BigNox\VirtualBox Guest Additions",
        ]:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                    install_dir, _ = winreg.QueryValueEx(key, "InstallDir")
                    # install_dir is typically "X:\Program Files\Nox\bin\"
                    adb_path = os.path.join(install_dir, "nox_adb.exe")
                    if os.path.isfile(adb_path):
                        return adb_path
            except (FileNotFoundError, OSError):
                continue
    except ImportError:
        pass  # winreg not available (non-Windows)

    # Ultimate fallback: return legacy hardcoded path
    return r"D:\Program Files\Nox\bin\nox_adb.exe"


def _find_bluestacks_adb() -> str:
    """Auto-detect HD-Adb.exe from common BlueStacks install locations."""
    candidates = [
        r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe",
        r"C:\Program Files (x86)\BlueStacks_nxt\HD-Adb.exe",
        r"D:\Program Files\BlueStacks_nxt\HD-Adb.exe",
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    # Fallback: system PATH adb (BlueStacks often registers it)
    system_adb = shutil.which("adb")
    if system_adb:
        return system_adb
    return "adb"


# Emulator presets — switch by changing ACTIVE_EMULATOR
EMULATOR_PRESETS = {
    "bluestacks": {"adb_path": _find_bluestacks_adb(), "port": 5555},
    "nox":        {"adb_path": _find_nox_adb(),        "port": 62001},
}
ACTIVE_EMULATOR = "bluestacks"

# ADB — resolved from active emulator preset
ADB_HOST = "127.0.0.1"
ADB_PORT = EMULATOR_PRESETS[ACTIVE_EMULATOR]["port"]
ADB_PATH = EMULATOR_PRESETS[ACTIVE_EMULATOR]["adb_path"]

# Screenshot
SCREENSHOT_DIR = "data/screenshots"

# Resolution (detected from Nox emulator: portrait 1080x1920)
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 1920

# Timing
LOOP_INTERVAL = 0.5          # seconds between main loop iterations

# Template matching
TEMPLATE_MATCH_THRESHOLD = 0.8

# Grid overlay
GRID_COLS = 8
GRID_ROWS = 6

# Paths
TEMPLATE_DIR = "templates"
STATE_FILE = "data/game_state.json"
NAV_PATHS_FILE = "data/navigation_paths.json"

# Multi-game support
GAMES_DIR = "games"
ACTIVE_GAME = "westgame2"
GAME_PACKAGES = {
    "frozenisland": "leyi.frozenislandpro",
    "westgame2": "leyi.cowboyclash3",
}
GAME_PACKAGE = GAME_PACKAGES[ACTIVE_GAME]

# Logging
LOG_DIR = "logs"

# Phase 5: Hardening
STUCK_MAX_SAME_SCENE = 10       # Trigger stuck recovery after N identical scenes
ADB_RECONNECT_RETRIES = 3       # Max ADB reconnection attempts
ACTION_MAX_RETRIES = 3           # Max retries per failed action
