"""
Notification System for PyCraftHub
Sends Discord notifications for server events
"""
import requests
import json
import os
from datetime import datetime

def load_settings():
    """Load settings to get webhook URL"""
    settings_file = "data/settings.json"
    
    if not os.path.exists(settings_file):
        return {}
    
    try:
        with open(settings_file, "r") as f:
            return json.load(f)
    except:
        return {}

def send_discord_notification(title, message, color=None):
    """
    Send a notification to Discord webhook
    
    Args:
        title: Notification title
        message: Notification message
        color: Embed color (int) - Green=3066993, Red=15158332, Yellow=16776960
    """
    settings = load_settings()
    
    # Check if notifications are enabled
    if not settings.get('notifications_enabled', True):
        return False
    
    webhook_url = settings.get('discord_webhook', '')
    
    if not webhook_url:
        return False
    
    try:
        # Create rich embed
        embed = {
            "title": title,
            "description": message,
            "color": color or 3447003,  # Blue by default
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "PyCraftHub v3.0"
            }
        }
        
        data = {
            "embeds": [embed]
        }
        
        response = requests.post(webhook_url, json=data, timeout=5)
        return response.status_code == 204
        
    except Exception as e:
        print(f"⚠ Notification failed: {e}")
        return False

def notify_server_start(server_name, port, server_type):
    """Notify when server starts"""
    title = "🟢 Server Started"
    message = f"""
**Server:** {server_name}
**Type:** {server_type.upper()}
**Port:** {port}
**Status:** Online and ready for players
"""
    send_discord_notification(title, message, color=3066993)  # Green

def notify_server_stop(server_name):
    """Notify when server stops"""
    title = "⚪ Server Stopped"
    message = f"""
**Server:** {server_name}
**Status:** Server has been shut down
"""
    send_discord_notification(title, message, color=16776960)  # Yellow

def notify_server_crash(server_name, error_msg=""):
    """Notify when server crashes"""
    title = "🔴 Server Crashed!"
    message = f"""
**Server:** {server_name}
**Status:** Server encountered an error and stopped
**Error:** {error_msg if error_msg else "Unknown error"}
"""
    send_discord_notification(title, message, color=15158332)  # Red

def notify_server_created(server_name, server_type, version):
    """Notify when new server is created"""
    title = "🆕 New Server Created"
    message = f"""
**Server:** {server_name}
**Type:** {server_type.upper()}
**Version:** {version}
**Status:** Server created successfully
"""
    send_discord_notification(title, message, color=5763719)  # Purple

def notify_server_deleted(server_name):
    """Notify when server is deleted"""
    title = "🗑️ Server Deleted"
    message = f"""
**Server:** {server_name}
**Status:** Server has been permanently deleted
"""
    send_discord_notification(title, message, color=10038562)  # Dark Red

def send_test_notification():
    """Send a test notification"""
    title = "✅ Test Notification"
    message = """
This is a test notification from PyCraftHub.
If you're seeing this, your webhook is configured correctly!
"""
    return send_discord_notification(title, message, color=3066993)
