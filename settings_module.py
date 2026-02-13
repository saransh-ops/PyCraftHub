"""
Settings Module for PyCraftHub
Handles user preferences, themes, and configuration
"""
import os
import json

SETTINGS_FILE = "data/settings.json"

DEFAULT_SETTINGS = {
    "theme": "cyan",  # cyan, green, blue, magenta, red
    "server_directory": "servers",
    "notifications_enabled": True,
    "discord_webhook": "",
    "auto_backup": False,
    "backup_interval": "daily",  # daily, weekly, manual
    "playit_enabled": False,
    "playit_secret": "",
    "auto_update_check": True,
    "show_splash": True,
    "default_ram": "2G",
    "default_difficulty": "normal"
}

def load_settings():
    """Load settings from file"""
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    
    try:
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        # Merge with defaults in case new settings were added
        for key, value in DEFAULT_SETTINGS.items():
            if key not in settings:
                settings[key] = value
        return settings
    except:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save settings to file"""
    os.makedirs("data", exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def get_theme_color(theme_name):
    """Get Fore color based on theme name"""
    from colorama import Fore
    
    themes = {
        "cyan": Fore.CYAN,
        "green": Fore.GREEN,
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
        "red": Fore.RED,
        "yellow": Fore.YELLOW
    }
    
    return themes.get(theme_name, Fore.CYAN)
