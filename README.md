# PyCraftHub v3.0

**A Python-based Minecraft server management tool for Windows**

Easily create, manage, and monitor Minecraft servers locally.

---

## Features

### Server Types Supported
- Paper (High-performance, plugin support)
- Purpur (Paper fork with optimizations)
- Vanilla (Pure Minecraft)
- Fabric (Lightweight mods)
- Forge (Mod loader)

### Core Features
- Create servers with guided setup
- Start, stop, and restart management
- Real-time performance monitoring
- Plugin and mod installer (Modrinth integration)
- World import and seed configuration
- Customizable settings and themes
- Discord webhook notifications

### Interface
- Colored command-line interface
- 6 color theme options
- Live server status display
- Interactive menus

---

## Requirements

- Python 3.10 or higher
- Java 17 or higher
- Windows operating system
- Internet connection for downloads

---

## Installation

1. Download the latest release
2. Extract to a folder
3. Run `PyCraftHubLauncher.bat`
4. Dependencies install automatically

---

## Quick Start

1. Launch PyCraftHub
2. Select "Create New Server"
3. Choose server type and configure settings
4. Start your server
5. Connect using the displayed local IP address

---

## Configuration

Access settings to customize:
- Color themes
- Server directories
- Default RAM allocation
- Notification preferences
- Network settings

---

## Server Management

### Starting Servers
- Interactive console window
- Live performance monitoring
- Auto-close helper windows

### Stopping Servers
- Graceful shutdown process
- Automatic cleanup
- Multiple stop methods

### Editing Servers
- Change RAM allocation
- Modify difficulty settings
- Install or remove mods/plugins
- Update world configuration

---

## Mods and Plugins

### Plugin Support (Paper/Purpur)
Search and install from Modrinth database with automatic dependency resolution.

### Mod Support (Fabric/Forge)
Version-compatible mod installation with dependency handling.

---

## Documentation

Built-in help system accessible from main menu includes:
- Server type comparisons
- Installation tutorials
- Configuration guides
- Troubleshooting tips

---

## Support

- Discord Community Server
- GitHub Issues
- Built-in documentation

---

## Project Structure

```
PyCraftHub/
├── main.py
├── core/
│   └── server_manager.py
├── servers/
├── data/
└── requirements.txt
```

---

## Technical Details

### Dependencies
- requests
- psutil
- colorama

### File Management
- JSON-based configuration
- Automatic backup of settings
- Clean directory structure

---

## License

Open Source

---

## Credits

Created by Saransh

Special thanks to the Minecraft server software teams and the Modrinth project.

---

## Version History

### Version 3.0
- Added Purpur and Forge support
- New colored interface
- Performance monitoring
- Discord notifications
- Settings system
- World configuration options

### Version 2.0
- Fabric server support
- Modrinth API integration
- Plugin/mod installer
- Improved server management

---

For detailed changelog, see CHANGELOG.txt