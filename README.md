<div align="center">

```
██████╗ ██╗   ██╗ ██████╗██████╗  █████╗ ███████╗████████╗██╗  ██╗██╗   ██╗██████╗ 
██╔══██╗╚██╗ ██╔╝██╔════╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██║  ██║██║   ██║██╔══██╗
██████╔╝ ╚████╔╝ ██║     ██████╔╝███████║█████╗     ██║   ███████║██║   ██║██████╔╝
██╔═══╝   ╚██╔╝  ██║     ██╔══██╗██╔══██║██╔══╝     ██║   ██╔══██║██║   ██║██╔══██╗
██║        ██║   ╚██████╗██║  ██║██║  ██║██║        ██║   ██║  ██║╚██████╔╝██████╔╝
╚═╝        ╚═╝    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝        ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ 
```

**Python-powered Minecraft server management. Create, monitor, and control — all from your terminal.**

[![Stars](https://img.shields.io/github/stars/saransh-ops/PyCraftHub?style=for-the-badge&color=00f5d4&labelColor=0e0e1a)](https://github.com/saransh-ops/PyCraftHub/stargazers)
[![License](https://img.shields.io/github/license/saransh-ops/PyCraftHub?style=for-the-badge&color=7c3aed&labelColor=0e0e1a)](LICENSE)
[![Release](https://img.shields.io/github/v/release/saransh-ops/PyCraftHub?style=for-the-badge&color=00f5d4&labelColor=0e0e1a)](https://github.com/saransh-ops/PyCraftHub/releases)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=0e0e1a)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white&labelColor=0e0e1a)](https://github.com/saransh-ops/PyCraftHub/releases)

</div>

---

## What is PyCraftHub?

PyCraftHub is an open-source terminal-based Minecraft server manager built in Python. Instead of downloading separate tools, editing config files by hand, or fighting the command line — you get a single guided interface that handles everything: server creation, plugin installs, live monitoring, and Discord alerts.

No prior server experience needed. Just run the `.bat` file and follow the menus.

---

## Features

### Server Types
| Type | Description | Best For |
|------|-------------|----------|
| ⚡ **Paper** | High-performance fork, best plugin compat | Survival, SMP |
| 💜 **Purpur** | Paper fork with extra gameplay tweaks | Custom SMP |
| 🌐 **Vanilla** | Pure, unmodified Minecraft | Authentic play |
| 🧵 **Fabric** | Lightweight, fast-updating mod loader | Performance mods |
| 🔧 **Forge** | Classic modding platform, largest ecosystem | Heavy modpacks |

### Core
- **Guided setup wizard** — RAM, world seed, difficulty, server type, all in one flow
- **Live performance monitor** — real-time CPU, RAM, and TPS via `psutil`
- **Modrinth integration** — search and install plugins/mods directly, auto-resolves dependencies
- **Discord webhook alerts** — get notified on start, stop, crashes, and player joins
- **World import & seed config** — bring your existing worlds or generate with a specific seed
- **6 color themes** — switch the terminal interface theme from settings anytime
- **JSON-based config** — clean, human-readable settings with automatic backups

---

## Requirements

- Python `3.10+`
- Java `17+`
- Windows OS
- Internet connection (for initial JAR downloads)

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/saransh-ops/PyCraftHub.git
cd PyCraftHub

# 2. Run the launcher — installs dependencies automatically
PyCraftHub launcher.bat
```

Or just **[download the latest release](https://github.com/saransh-ops/PyCraftHub/releases)**, extract, and double-click `PyCraftHub launcher.bat`. That's it.

---

## Quick Start

```
[1] Create New Server    ← Pick this first
[2] Manage Servers
[3] Settings
[4] Help
```

1. Select **Create New Server**
2. Choose your server type (Paper, Purpur, Vanilla, Fabric, or Forge)
3. Set your RAM allocation and world seed
4. Hit **Start** — your local IP is displayed instantly
5. Share the IP with friends and connect

---

## Project Structure

```
PyCraftHub/
├── main.py                   # Entry point & main menu
├── notifications.py          # Discord webhook system
├── server_watcher.py         # Live performance monitoring
├── settings_module.py        # Settings & theme management
├── requirements.txt          # Python dependencies
├── PyCraftHub launcher.bat   # Windows launcher (auto-installs deps)
├── core/
│   └── server_manager.py     # Server create / start / stop / edit
├── data/                     # Server JARs, configs, cached data
└── utils/                    # Shared utilities
```

---

## Dependencies

```txt
requests    # API calls (Modrinth, download JARs)
psutil      # Live CPU / RAM monitoring
colorama    # Colored terminal output
```

All installed automatically on first launch.

---

## Changelog

### v3.0 — Latest
- Added **Purpur** server support
- Added **Forge** server support
- New colored CLI interface with 6 switchable themes
- Live performance monitoring (CPU, RAM, TPS)
- Discord webhook notifications
- Full settings system
- World seed & import configuration

### v2.0
- Fabric server support
- Modrinth API integration
- Plugin/mod installer with dependency resolution
- Improved server management flow

---

## Contributing

Contributions are welcome. Open an issue first to discuss what you'd like to change, then submit a PR.

```bash
# Fork → clone → create branch → make changes → PR
git checkout -b feature/your-feature-name
```

---

## Support

- 🐛 **Bug reports** → [GitHub Issues](https://github.com/saransh-ops/PyCraftHub/issues)
- 💬 **Discord** → `godkiller_saransh`
- 📖 **Built-in docs** → select `[4] Help` from the main menu

---

## License

MIT — free to use, modify, and distribute. See [LICENSE](LICENSE) for details.

---

<div align="center">

Made with 🩵 by [Saransh Gupta](https://github.com/saransh-ops)

*If this helped you, drop a ⭐ — it means a lot!*

</div>
