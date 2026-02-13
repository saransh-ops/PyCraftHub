import os
import sys

# Try to import colorama, fallback to no colors if not available
try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    print("⚠ Colorama not installed. Running without colors.")
    print("Install with: pip install colorama --break-system-packages")
    HAS_COLOR = False
    class Fore:
        CYAN = LIGHTCYAN_EX = LIGHTBLUE_EX = BLUE = ""
        GREEN = LIGHTGREEN_EX = ""
        YELLOW = LIGHTYELLOW_EX = ""
        RED = LIGHTRED_EX = ""
        WHITE = LIGHTWHITE_EX = ""
        MAGENTA = LIGHTMAGENTA_EX = ""
    class Style:
        BRIGHT = RESET_ALL = ""
    class Back:
        pass

from core.server_manager import (
    create_server, edit_server, start_server,
    stop_server, restart_server, delete_server,
    list_servers, load_data, list_installed_mods
)

# Import settings module
try:
    from settings_module import load_settings, save_settings, get_theme_color
    settings = load_settings()
    THEME_COLOR = get_theme_color(settings.get("theme", "cyan"))
except:
    settings = {}
    THEME_COLOR = Fore.CYAN

# Try to import is_server_running
try:
    from core.server_manager import is_server_running
except ImportError:
    def is_server_running(server_name):
        path = f"servers/{server_name}"
        running_file = os.path.join(path, "running.txt")
        return os.path.exists(running_file)

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def splash():
    """Display splash screen with FIXED ASCII art"""
    clear_screen()
    
    logo = r"""
╔════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                        ║
║   ██████╗ ██╗   ██╗ ██████╗██████╗  █████╗ ███████╗████████╗██╗  ██╗██╗   ██╗██████╗   ║
║   ██╔══██╗╚██╗ ██╔╝██╔════╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██║  ██║██║   ██║██╔══██╗  ║
║   ██████╔╝ ╚████╔╝ ██║     ██████╔╝███████║█████╗     ██║   ███████║██║   ██║██████╔╝  ║
║   ██╔═══╝   ╚██╔╝  ██║     ██╔══██╗██╔══██║██╔══╝     ██║   ██╔══██║██║   ██║██╔══██╗  ║
║   ██║        ██║   ╚██████╗██║  ██║██║  ██║██║        ██║   ██║  ██║╚██████╔╝██████╔╝  ║
║   ╚═╝        ╚═╝    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝        ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝   ║
║                                                                                        ║
║                    » Minecraft Server Management Suite «                               ║
║                           Version 3.0 | by Saransh                                     ║
║                                                                                        ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
"""
    
    print(THEME_COLOR + Style.BRIGHT + logo)
    print(Fore.YELLOW + "                      ⚡ Powered by Python | Open Source ⚡")
    print()
    input(Fore.GREEN + "                      Press ENTER to continue...")

def print_header(title):
    """Print a styled header"""
    width = 78
    print("\n" + THEME_COLOR + "╔" + "═" * width + "╗")
    print(THEME_COLOR + "║" + Style.BRIGHT + Fore.WHITE + title.center(width) + THEME_COLOR + "║")
    print(THEME_COLOR + "╚" + "═" * width + "╝")

def print_server_card(name, info, index):
    """Print a beautiful server card"""
    status = "🟢 RUNNING" if is_server_running(name) else "⚪ STOPPED"
    status_color = Fore.GREEN if "RUNNING" in status else Fore.WHITE
    
    print(f"\n{THEME_COLOR}┌─ Server #{index} " + "─" * 60 + "┐")
    print(f"{THEME_COLOR}│ {Fore.YELLOW}Name:{Fore.WHITE} {name:<30} {status_color}{status:<20}{THEME_COLOR}│")
    print(f"{THEME_COLOR}│ {Fore.YELLOW}Type:{Fore.WHITE} {info['type'].upper():<15} "
          f"{Fore.YELLOW}Version:{Fore.WHITE} {info['version']:<15} "
          f"{Fore.YELLOW}RAM:{Fore.WHITE} {info['ram']:<10}{THEME_COLOR}│")
    print(f"{THEME_COLOR}│ {Fore.YELLOW}Port:{Fore.WHITE} {info['port']:<15} "
          f"{Fore.YELLOW}Difficulty:{Fore.WHITE} {info.get('difficulty', 'normal').capitalize():<20}{THEME_COLOR}│")
    
    online_mode = info.get('online_mode', 'true')
    mode_text = "🔒 Premium Only" if online_mode == "true" else "🔓 Cracked Allowed"
    mode_color = Fore.BLUE if online_mode == "true" else Fore.MAGENTA
    print(f"{THEME_COLOR}│ {mode_color}{mode_text:<67}{THEME_COLOR}│")
    
    print(f"{THEME_COLOR}└" + "─" * 70 + "┘")

def show_quick_actions():
    """Show quick action buttons"""
    print(f"\n{THEME_COLOR}╭─ Quick Actions " + "─" * 58 + "╮")
    print(f"{THEME_COLOR}│ {Fore.GREEN}[S]{Fore.WHITE} Start  "
          f"{Fore.RED}[X]{Fore.WHITE} Stop  "
          f"{Fore.YELLOW}[R]{Fore.WHITE} Restart  "
          f"{Fore.BLUE}[E]{Fore.WHITE} Edit  "
          f"{Fore.MAGENTA}[D]{Fore.WHITE} Delete  "
          f"{THEME_COLOR}[B]{Fore.WHITE} Back      {THEME_COLOR}│")
    print(f"{THEME_COLOR}╰" + "─" * 75 + "╯")

def server_management_menu():
    """Dedicated server management submenu"""
    while True:
        clear_screen()
        print_header("Server Management")
        
        data = load_data()
        if not data:
            print(f"\n{Fore.YELLOW}No servers available. Create one first!")
            input(f"\n{Fore.GREEN}Press ENTER to return...")
            return
        
        server_list = list(data.keys())
        for i, name in enumerate(server_list, 1):
            print_server_card(name, data[name], i)
        
        show_quick_actions()
        
        choice = input(f"\n{THEME_COLOR}Action: {Fore.WHITE}").strip().lower()
        
        if choice == 'b' or choice == '0':
            return
        
        print(f"\n{Fore.YELLOW}Enter server number: ", end="")
        sel = input().strip()
        
        if not sel.isdigit() or int(sel) < 1 or int(sel) > len(server_list):
            print(f"{Fore.RED}❌ Invalid selection")
            input(f"\n{Fore.YELLOW}Press ENTER to continue...")
            continue
        
        server_name = server_list[int(sel) - 1]
        
        if choice == 's':
            start_server(server_name)
        elif choice == 'x':
            stop_server(server_name)
        elif choice == 'r':
            restart_server(server_name)
        elif choice == 'e':
            edit_server()
        elif choice == 'd':
            confirm = input(f"\n{Fore.RED}⚠️  Delete '{server_name}'? This cannot be undone! (yes/no): {Fore.WHITE}")
            if confirm.lower() == 'yes':
                delete_server(server_name)
        else:
            print(f"{Fore.RED}❌ Invalid action")
        
        input(f"\n{Fore.GREEN}Press ENTER to continue...")

def server_tools_menu():
    """Server tools submenu - backup, monitoring, cleanup"""
    while True:
        clear_screen()
        print_header("Server Tools")
        
        print(f"\n{THEME_COLOR}╭─ Available Tools " + "─" * 57 + "╮")
        print(f"{THEME_COLOR}│                                                                        │")
        print(f"{THEME_COLOR}│  {Fore.GREEN}1.{Fore.WHITE} 📊 Server Performance Monitor                                    {THEME_COLOR}│")
        print(f"{THEME_COLOR}│  {Fore.GREEN}2.{Fore.WHITE} 💾 Backup Server                                                 {THEME_COLOR}│")
        print(f"{THEME_COLOR}│  {Fore.GREEN}3.{Fore.WHITE} ♻️  Restore from Backup                                          {THEME_COLOR}│")
        print(f"{THEME_COLOR}│  {Fore.GREEN}4.{Fore.WHITE} 🗑️  Clean Server Cache/Logs                                     {THEME_COLOR}│")
        print(f"{THEME_COLOR}│  {Fore.GREEN}5.{Fore.WHITE} 📤 Export Server                                                 {THEME_COLOR}│")
        print(f"{THEME_COLOR}│  {Fore.GREEN}6.{Fore.WHITE} 📥 Import Server Package                                         {THEME_COLOR}│")
        print(f"{THEME_COLOR}│  {Fore.GREEN}0.{Fore.WHITE} 🔙 Back to Main Menu                                             {THEME_COLOR}│")
        print(f"{THEME_COLOR}│                                                                        │")
        print(f"{THEME_COLOR}╰" + "─" * 75 + "╯")
        
        choice = input(f"\n{THEME_COLOR}» {Fore.WHITE}").strip()
        
        if choice == "0":
            return
        elif choice == "1":
            print(f"\n{Fore.YELLOW}📊 Performance Monitor")
            print(f"{Fore.WHITE}This feature will show real-time CPU, RAM, and TPS stats")
            print(f"{Fore.CYAN}🚧 Coming in v4.0 update!(along with a major drop)")
        elif choice == "2":
            print(f"\n{Fore.YELLOW}💾 Backup Server")
            print(f"{Fore.WHITE}Create compressed backups of your servers")
            print(f"{Fore.CYAN}🚧 Coming in v4.0 update!(along with a major drop)")
        elif choice == "3":
            print(f"\n{Fore.YELLOW}♻️  Restore from Backup")
            print(f"{Fore.WHITE}Restore your server from a previous backup")
            print(f"{Fore.CYAN}🚧 Coming in v4.0 update!(along with a major drop)")
        elif choice == "4":
            print(f"\n{Fore.YELLOW}🗑️  Clean Server Cache/Logs")
            print(f"{Fore.WHITE}Clear old logs and cache files to free up space")
            print(f"{Fore.CYAN}🚧 Coming in v4.0 update!(along with a major drop)")
        elif choice == "5":
            print(f"\n{Fore.YELLOW}📤 Export Server")
            print(f"{Fore.WHITE}Package your server for sharing or migration")
            print(f"{Fore.CYAN}🚧 Coming in v4.0 update!(along with a major drop)")
        elif choice == "6":
            print(f"\n{Fore.YELLOW}📥 Import Server Package")
            print(f"{Fore.WHITE}Import a server from a .zip package")
            print(f"{Fore.CYAN}🚧 Coming in v4.0 update!(along with a major drop)")
        else:
            print(f"{Fore.RED}❌ Invalid option")
        
        input(f"\n{Fore.GREEN}Press ENTER to continue...")

def show_about():
    """Show about/credits screen"""
    clear_screen()
    print_header("About PyCraftHub")
    
    about_text = f"""
{THEME_COLOR}╔══════════════════════════════════════════════════════════════════════════╗
{THEME_COLOR}║                                                                          ║
{THEME_COLOR}║  {Fore.YELLOW}PyCraftHub v3.0{Fore.WHITE} - Minecraft Server Management Suite                  {THEME_COLOR}║
{THEME_COLOR}║                                                                          ║
{THEME_COLOR}║  {Fore.WHITE}Created by: {Fore.GREEN}Saransh                                                    {THEME_COLOR}║
{THEME_COLOR}║  {Fore.WHITE}Language: {Fore.GREEN}Python 3.x                                                   {THEME_COLOR}║
{THEME_COLOR}║  {Fore.WHITE}License: {Fore.GREEN}Open Source                                                   {THEME_COLOR}║
{THEME_COLOR}║  {Fore.WHITE}GitHub: {Fore.CYAN}github.com/yourusername/pycrafthub                             {THEME_COLOR}║
{THEME_COLOR}║                                                                          ║
{THEME_COLOR}║  {Fore.YELLOW}✨ Features:{Fore.WHITE}                                                           {THEME_COLOR}║
{THEME_COLOR}║  {Fore.GREEN}✓{Fore.WHITE} Multi-server management (Paper, Vanilla, Fabric)                  {THEME_COLOR}║
{THEME_COLOR}║  {Fore.GREEN}✓{Fore.WHITE} Auto-updating plugin/mod installer via Modrinth                   {THEME_COLOR}║
{THEME_COLOR}║  {Fore.GREEN}✓{Fore.WHITE} Cracked player support (online-mode toggle)                       {THEME_COLOR}║
{THEME_COLOR}║  {Fore.GREEN}✓{Fore.WHITE} World import & custom seed configuration                          {THEME_COLOR}║
{THEME_COLOR}║  {Fore.GREEN}✓{Fore.WHITE} Health monitoring & auto-close helper windows                     {THEME_COLOR}║
{THEME_COLOR}║  {Fore.GREEN}✓{Fore.WHITE} Bedrock cross-play support via Geyser                             {THEME_COLOR}║
{THEME_COLOR}║  {Fore.GREEN}✓{Fore.WHITE} Customizable themes and settings                                  {THEME_COLOR}║
{THEME_COLOR}║  {Fore.GREEN}✓{Fore.WHITE} Discord notifications (webhook integration)                       {THEME_COLOR}║
{THEME_COLOR}║  {Fore.GREEN}✓{Fore.WHITE} Interactive server console with command support                  {THEME_COLOR}║
{THEME_COLOR}║                                                                          ║
{THEME_COLOR}║  {Fore.YELLOW}🎯 What's New in v3.0:{Fore.WHITE}                                                {THEME_COLOR}║
{THEME_COLOR}║  • Beautiful colored CLI with multiple themes                           {THEME_COLOR}║
{THEME_COLOR}║  • Complete settings system with persistence                            {THEME_COLOR}║
{THEME_COLOR}║  • World setup wizard (import/seed/random)                              {THEME_COLOR}║
{THEME_COLOR}║  • Enhanced server management hub                                       {THEME_COLOR}║
{THEME_COLOR}║  • Auto-closing helper windows                                          {THEME_COLOR}║
{THEME_COLOR}║                                                                          ║
{THEME_COLOR}║  {Fore.YELLOW}💖 Made with ❤️  using Python{Fore.WHITE}                                         {THEME_COLOR}║
{THEME_COLOR}║                                                                          ║
{THEME_COLOR}║  {Fore.CYAN}Special thanks to:{Fore.WHITE}                                                     {THEME_COLOR}║
{THEME_COLOR}║  • Minecraft community for server software                              {THEME_COLOR}║
{THEME_COLOR}║  • PaperMC, Fabric, and Modrinth teams                                  {THEME_COLOR}║
{THEME_COLOR}║  • All contributors and testers                                         {THEME_COLOR}║
{THEME_COLOR}║                                                                          ║
{THEME_COLOR}╚══════════════════════════════════════════════════════════════════════════╝
"""
    print(about_text)
    input(f"\n{Fore.GREEN}Press ENTER to continue...")

def show_documentation():
    """Show comprehensive documentation"""
    clear_screen()
    print_header("PyCraftHub Documentation")
    
    docs = f"""
{Fore.YELLOW}═══════════════════════════════════════════════════════════════════════{Fore.WHITE}
                          📖 QUICK START GUIDE
{Fore.YELLOW}═══════════════════════════════════════════════════════════════════════{Fore.WHITE}

{Fore.CYAN}━━━ 1. Creating Your First Server ━━━{Fore.WHITE}

   {Fore.GREEN}Step 1:{Fore.WHITE} Select "Create New Server" from main menu
   {Fore.GREEN}Step 2:{Fore.WHITE} Choose server type:
           • {Fore.YELLOW}Paper{Fore.WHITE} - Recommended for plugins (most popular)
           • {Fore.YELLOW}Vanilla{Fore.WHITE} - Pure Minecraft, no modifications
           • {Fore.YELLOW}Fabric{Fore.WHITE} - For client & server-side mods

   {Fore.GREEN}Step 3:{Fore.WHITE} Configure basic settings:
           • RAM allocation (recommended: 2G minimum)
           • Difficulty (Peaceful/Easy/Normal/Hard)
           • Render distance (8-12 recommended)

   {Fore.GREEN}Step 4:{Fore.WHITE} Optional configurations:
           • Allow cracked players (y/n)
           • World type (Normal/Flat/Amplified/Large Biomes)
           • World setup (Import/Custom Seed/Random)

   {Fore.GREEN}Step 5:{Fore.WHITE} Install extras (if applicable):
           • Geyser for Bedrock cross-play
           • Recommended plugins/mods
           • Search Modrinth for more

{Fore.CYAN}━━━ 2. Managing Servers ━━━{Fore.WHITE}

   {Fore.YELLOW}Quick Actions:{Fore.WHITE}
   • Use "Manage Servers" menu for one-stop control
   • Keyboard shortcuts: [S]tart, [X]Stop, [R]estart, [E]dit, [D]elete

   {Fore.YELLOW}Starting a Server:{Fore.WHITE}
   • Opens 3 windows:
     1. {Fore.GREEN}Server Console{Fore.WHITE} - Interactive Minecraft console
     2. {Fore.CYAN}Health Monitor{Fore.WHITE} - CPU/RAM usage (auto-closes)
     3. {Fore.BLUE}Watcher{Fore.WHITE} - Manages shutdown (auto-closes)

   {Fore.YELLOW}Stopping a Server:{Fore.WHITE}
   • Use PyCraftHub menu for graceful shutdown
   • Or type "/stop" in server console
   • Helper windows close automatically

{Fore.CYAN}━━━ 3. Installing Plugins & Mods ━━━{Fore.WHITE}

   {Fore.YELLOW}Paper Servers (Plugins):{Fore.WHITE}
   1. Edit your server
   2. Go to Mods/Plugins menu
   3. Choose "Install Recommended Plugins" or search Modrinth
   4. Popular choices: EssentialsX, ViaVersion, LuckPerms

   {Fore.YELLOW}Fabric Servers (Mods):{Fore.WHITE}
   1. Install Fabric API first (prompted during creation)
   2. Use mod search to find compatible mods
   3. Dependencies are auto-installed
   4. Popular: Sodium, Lithium, Simple Voice Chat

{Fore.CYAN}━━━ 4. World Configuration ━━━{Fore.WHITE}

   {Fore.YELLOW}Importing Worlds:{Fore.WHITE}
   • From Singleplayer: Select your saves folder
   • From Another Server: Select world, world_nether, world_the_end

   {Fore.YELLOW}Custom Seeds:{Fore.WHITE}
   • Enter any text or number as seed
   • Examples: "Village", "12345", "-8675309"
   • Creates predictable world generation

   {Fore.YELLOW}World Types:{Fore.WHITE}
   • Normal - Standard terrain
   • Flat - Superflat for creative builds
   • Large Biomes - Massive biome sizes
   • Amplified - Extreme terrain generation

{Fore.CYAN}━━━ 5. Advanced Features ━━━{Fore.WHITE}

   {Fore.YELLOW}Cracked Player Support:{Fore.WHITE}
   • Allows non-premium Minecraft accounts
   • Disables Mojang authentication
   • ⚠️  Security risk - use authentication plugins (AuthMe)

   {Fore.YELLOW}Geyser (Bedrock Cross-Play):{Fore.WHITE}
   • Allows Bedrock Edition players to join Java servers
   • Requires UDP tunnel on port 19132 (use Playit.gg)
   • Auto-installed with Floodgate for authentication

   {Fore.YELLOW}Playit.gg Integration:{Fore.WHITE}
   • Free port forwarding/tunneling service
   • No router configuration needed
   • Configure in Settings → Network Settings

{Fore.CYAN}━━━ 6. Settings & Customization ━━━{Fore.WHITE}

   {Fore.YELLOW}Themes:{Fore.WHITE} Choose from 6 color schemes
   {Fore.YELLOW}Notifications:{Fore.WHITE} Discord webhooks for server events
   {Fore.YELLOW}Backups:{Fore.WHITE} Automated daily/weekly backups (coming soon)
   {Fore.YELLOW}Defaults:{Fore.WHITE} Set default RAM and difficulty for new servers

{Fore.CYAN}━━━ 7. Troubleshooting ━━━{Fore.WHITE}

   {Fore.RED}Problem:{Fore.WHITE} Server won't start
   {Fore.GREEN}Solution:{Fore.WHITE} Check server.jar exists, verify Java is installed

   {Fore.RED}Problem:{Fore.WHITE} Can't connect to server
   {Fore.GREEN}Solution:{Fore.WHITE} Check firewall, use local IP (shown on start)

   {Fore.RED}Problem:{Fore.WHITE} Server crashes immediately
   {Fore.GREEN}Solution:{Fore.WHITE} Check console for errors, verify RAM isn't too high

   {Fore.RED}Problem:{Fore.WHITE} Plugins/mods not working
   {Fore.GREEN}Solution:{Fore.WHITE} Ensure compatibility with your Minecraft version

{Fore.CYAN}━━━ 8. Keyboard Shortcuts ━━━{Fore.WHITE}

   {Fore.YELLOW}Server Management:{Fore.WHITE}
   • S - Start server
   • X - Stop server  
   • R - Restart server
   • E - Edit server
   • D - Delete server
   • B - Back to menu

{Fore.YELLOW}═══════════════════════════════════════════════════════════════════════{Fore.WHITE}
                    💡 TIP: Press 0 from any menu to go back!
{Fore.YELLOW}═══════════════════════════════════════════════════════════════════════{Fore.WHITE}
"""
    print(docs)
    input(f"\n{Fore.GREEN}Press ENTER to continue...")

def settings_menu():
    """Complete settings menu with all features"""
    global settings, THEME_COLOR
    
    while True:
        clear_screen()
        print_header("Settings & Configuration")
        
        # Display current settings
        print(f"\n{THEME_COLOR}╭─ Current Settings " + "─" * 56 + "╮")
        print(f"{THEME_COLOR}│ {Fore.YELLOW}Theme:{Fore.WHITE} {settings.get('theme', 'cyan').capitalize():<20} "
              f"{Fore.YELLOW}Notifications:{Fore.WHITE} {'Enabled' if settings.get('notifications_enabled') else 'Disabled':<20}{THEME_COLOR}│")
        print(f"{THEME_COLOR}│ {Fore.YELLOW}Auto-Backup:{Fore.WHITE} {'Enabled' if settings.get('auto_backup') else 'Disabled':<13} "
              f"{Fore.YELLOW}Server Dir:{Fore.WHITE} {settings.get('server_directory', 'servers'):<25}{THEME_COLOR}│")
        print(f"{THEME_COLOR}╰" + "─" * 75 + "╯")
        
        # Menu options
        print(f"\n{THEME_COLOR}╭─ Configuration Options " + "─" * 51 + "╮")
        print(f"{THEME_COLOR}│                                                                        │")
        print(f"{THEME_COLOR}│  {Fore.GREEN}1.{Fore.WHITE} 🎨 Change Color Theme                                            {THEME_COLOR}│")
        print(f"{THEME_COLOR}│  {Fore.GREEN}2.{Fore.WHITE} 📁 Set Server Directory                                          {THEME_COLOR}│")
        print(f"{THEME_COLOR}│  {Fore.GREEN}3.{Fore.WHITE} 🔔 Configure Notifications                                       {THEME_COLOR}│")
        print(f"{THEME_COLOR}│  {Fore.GREEN}4.{Fore.WHITE} 🌐 Network Settings (Playit.gg)                                  {THEME_COLOR}│")
        print(f"{THEME_COLOR}│  {Fore.GREEN}5.{Fore.WHITE} 💾 Backup Settings                                               {THEME_COLOR}│")
        print(f"{THEME_COLOR}│  {Fore.GREEN}6.{Fore.WHITE} ⚙️  Default Server Settings                                      {THEME_COLOR}│")
        print(f"{THEME_COLOR}│  {Fore.GREEN}7.{Fore.WHITE} 🔄 Reset to Defaults                                             {THEME_COLOR}│")
        print(f"{THEME_COLOR}│  {Fore.GREEN}0.{Fore.WHITE} 🔙 Back to Main Menu                                             {THEME_COLOR}│")
        print(f"{THEME_COLOR}│                                                                        │")
        print(f"{THEME_COLOR}╰" + "─" * 75 + "╯")
        
        choice = input(f"\n{THEME_COLOR}» {Fore.WHITE}").strip()
        
        if choice == "0":
            return
            
        elif choice == "1":
            # Change theme
            clear_screen()
            print_header("Select Color Theme")
            
            themes = ["cyan", "green", "blue", "magenta", "red", "yellow"]
            
            print(f"\n{THEME_COLOR}Available themes:")
            for i, theme in enumerate(themes, 1):
                color = get_theme_color(theme)
                print(f"{color}{i}. {theme.capitalize()} Theme")
            
            theme_choice = input(f"\n{Fore.YELLOW}Select theme (1-{len(themes)}): {Fore.WHITE}").strip()
            
            if theme_choice.isdigit() and 1 <= int(theme_choice) <= len(themes):
                selected_theme = themes[int(theme_choice) - 1]
                settings['theme'] = selected_theme
                THEME_COLOR = get_theme_color(selected_theme)
                save_settings(settings)
                print(f"\n{Fore.GREEN}✔ Theme changed to {selected_theme.capitalize()}!")
            else:
                print(f"\n{Fore.RED}❌ Invalid choice")
            
            input(f"\n{Fore.YELLOW}Press ENTER to continue...")
            
        elif choice == "2":
            # Set server directory
            clear_screen()
            print_header("Server Directory")
            
            print(f"\n{Fore.YELLOW}Current directory:{Fore.WHITE} {settings.get('server_directory', 'servers')}")
            print(f"\n{Fore.WHITE}Enter new directory (or press ENTER to keep current):")
            
            new_dir = input(f"{THEME_COLOR}» {Fore.WHITE}").strip()
            
            if new_dir:
                settings['server_directory'] = new_dir
                save_settings(settings)
                
                # Create directory if it doesn't exist
                os.makedirs(new_dir, exist_ok=True)
                
                print(f"\n{Fore.GREEN}✔ Server directory set to: {new_dir}")
            else:
                print(f"\n{Fore.YELLOW}Directory unchanged")
            
            input(f"\n{Fore.YELLOW}Press ENTER to continue...")
            
        elif choice == "3":
            # Configure notifications
            clear_screen()
            print_header("Notification Settings")
            
            print(f"\n{THEME_COLOR}╭─ Notification Options " + "─" * 52 + "╮")
            print(f"{THEME_COLOR}│  {Fore.GREEN}1.{Fore.WHITE} Toggle Notifications (Currently: "
                  f"{'Enabled' if settings.get('notifications_enabled') else 'Disabled'})       {THEME_COLOR}│")
            print(f"{THEME_COLOR}│  {Fore.GREEN}2.{Fore.WHITE} Set Discord Webhook URL                                      {THEME_COLOR}│")
            print(f"{THEME_COLOR}│  {Fore.GREEN}3.{Fore.WHITE} Test Notification                                            {THEME_COLOR}│")
            print(f"{THEME_COLOR}│  {Fore.GREEN}0.{Fore.WHITE} Back                                                         {THEME_COLOR}│")
            print(f"{THEME_COLOR}╰" + "─" * 75 + "╯")
            
            notif_choice = input(f"\n{THEME_COLOR}» {Fore.WHITE}").strip()
            
            if notif_choice == "1":
                settings['notifications_enabled'] = not settings.get('notifications_enabled', True)
                save_settings(settings)
                status = "enabled" if settings['notifications_enabled'] else "disabled"
                print(f"\n{Fore.GREEN}✔ Notifications {status}")
                input(f"\n{Fore.YELLOW}Press ENTER to continue...")
                
            elif notif_choice == "2":
                print(f"\n{Fore.YELLOW}Enter Discord Webhook URL:")
                webhook = input(f"{THEME_COLOR}» {Fore.WHITE}").strip()
                
                if webhook:
                    settings['discord_webhook'] = webhook
                    save_settings(settings)
                    print(f"\n{Fore.GREEN}✔ Webhook URL saved")
                else:
                    print(f"\n{Fore.YELLOW}No URL entered")
                
                input(f"\n{Fore.YELLOW}Press ENTER to continue...")
                
            elif notif_choice == "3":
                print(f"\n{Fore.YELLOW}🔔 Sending test notification...")
                
                webhook_url = settings.get('discord_webhook', '')
                
                if webhook_url:
                    try:
                        import requests
                        data = {
                            "content": "🎮 PyCraftHub Test Notification - System is working!"
                        }
                        requests.post(webhook_url, json=data)
                        print(f"{Fore.GREEN}✔ Test notification sent!")
                    except Exception as e:
                        print(f"{Fore.RED}❌ Failed to send: {e}")
                else:
                    print(f"{Fore.RED}❌ No webhook URL configured")
                
                input(f"\n{Fore.YELLOW}Press ENTER to continue...")
            
        elif choice == "4":
            # Network settings
            clear_screen()
            print_header("Network Settings - Playit.gg Integration")
            
            print(f"\n{THEME_COLOR}╭─ Playit.gg Settings " + "─" * 54 + "╮")
            print(f"{THEME_COLOR}│  {Fore.GREEN}1.{Fore.WHITE} Toggle Playit.gg (Currently: "
                  f"{'Enabled' if settings.get('playit_enabled') else 'Disabled'})            {THEME_COLOR}│")
            print(f"{THEME_COLOR}│  {Fore.GREEN}2.{Fore.WHITE} Set Playit Secret Key                                        {THEME_COLOR}│")
            print(f"{THEME_COLOR}│  {Fore.GREEN}3.{Fore.WHITE} Open Playit.gg Website                                       {THEME_COLOR}│")
            print(f"{THEME_COLOR}│  {Fore.GREEN}0.{Fore.WHITE} Back                                                         {THEME_COLOR}│")
            print(f"{THEME_COLOR}╰" + "─" * 75 + "╯")
            
            network_choice = input(f"\n{THEME_COLOR}» {Fore.WHITE}").strip()
            
            if network_choice == "1":
                settings['playit_enabled'] = not settings.get('playit_enabled', False)
                save_settings(settings)
                status = "enabled" if settings['playit_enabled'] else "disabled"
                print(f"\n{Fore.GREEN}✔ Playit.gg {status}")
                input(f"\n{Fore.YELLOW}Press ENTER to continue...")
                
            elif network_choice == "2":
                print(f"\n{Fore.YELLOW}Enter Playit.gg Secret Key:")
                secret = input(f"{THEME_COLOR}» {Fore.WHITE}").strip()
                
                if secret:
                    settings['playit_secret'] = secret
                    save_settings(settings)
                    print(f"\n{Fore.GREEN}✔ Secret key saved")
                else:
                    print(f"\n{Fore.YELLOW}No key entered")
                
                input(f"\n{Fore.YELLOW}Press ENTER to continue...")
                
            elif network_choice == "3":
                import webbrowser
                webbrowser.open("https://playit.gg")
                print(f"\n{Fore.GREEN}✔ Opening Playit.gg in browser...")
                input(f"\n{Fore.YELLOW}Press ENTER to continue...")
            
        elif choice == "5":
            # Backup settings
            clear_screen()
            print_header("Backup Settings")
            
            print(f"\n{THEME_COLOR}╭─ Backup Configuration " + "─" * 52 + "╮")
            print(f"{THEME_COLOR}│  {Fore.GREEN}1.{Fore.WHITE} Toggle Auto-Backup (Currently: "
                  f"{'Enabled' if settings.get('auto_backup') else 'Disabled'})          {THEME_COLOR}│")
            print(f"{THEME_COLOR}│  {Fore.GREEN}2.{Fore.WHITE} Set Backup Interval (Currently: "
                  f"{settings.get('backup_interval', 'daily').capitalize()})                {THEME_COLOR}│")
            print(f"{THEME_COLOR}│  {Fore.GREEN}0.{Fore.WHITE} Back                                                         {THEME_COLOR}│")
            print(f"{THEME_COLOR}╰" + "─" * 75 + "╯")
            
            backup_choice = input(f"\n{THEME_COLOR}» {Fore.WHITE}").strip()
            
            if backup_choice == "1":
                settings['auto_backup'] = not settings.get('auto_backup', False)
                save_settings(settings)
                status = "enabled" if settings['auto_backup'] else "disabled"
                print(f"\n{Fore.GREEN}✔ Auto-backup {status}")
                input(f"\n{Fore.YELLOW}Press ENTER to continue...")
                
            elif backup_choice == "2":
                print(f"\n{Fore.YELLOW}Select backup interval:")
                print(f"{THEME_COLOR}1. Daily")
                print(f"{THEME_COLOR}2. Weekly")
                print(f"{THEME_COLOR}3. Manual only")
                
                interval_choice = input(f"\n{THEME_COLOR}» {Fore.WHITE}").strip()
                
                intervals = {"1": "daily", "2": "weekly", "3": "manual"}
                
                if interval_choice in intervals:
                    settings['backup_interval'] = intervals[interval_choice]
                    save_settings(settings)
                    print(f"\n{Fore.GREEN}✔ Backup interval set to: {intervals[interval_choice]}")
                else:
                    print(f"\n{Fore.RED}❌ Invalid choice")
                
                input(f"\n{Fore.YELLOW}Press ENTER to continue...")
            
        elif choice == "6":
            # Default server settings
            clear_screen()
            print_header("Default Server Settings")
            
            print(f"\n{THEME_COLOR}╭─ Set Defaults " + "─" * 60 + "╮")
            print(f"{THEME_COLOR}│  {Fore.GREEN}1.{Fore.WHITE} Default RAM (Current: {settings.get('default_ram', '2G')})                        {THEME_COLOR}│")
            print(f"{THEME_COLOR}│  {Fore.GREEN}2.{Fore.WHITE} Default Difficulty (Current: {settings.get('default_difficulty', 'normal').capitalize()})              {THEME_COLOR}│")
            print(f"{THEME_COLOR}│  {Fore.GREEN}0.{Fore.WHITE} Back                                                         {THEME_COLOR}│")
            print(f"{THEME_COLOR}╰" + "─" * 75 + "╯")
            
            default_choice = input(f"\n{THEME_COLOR}» {Fore.WHITE}").strip()
            
            if default_choice == "1":
                print(f"\n{Fore.YELLOW}Enter default RAM (e.g., 2G, 4G, 8G):")
                ram = input(f"{THEME_COLOR}» {Fore.WHITE}").strip().upper()
                
                if ram:
                    settings['default_ram'] = ram
                    save_settings(settings)
                    print(f"\n{Fore.GREEN}✔ Default RAM set to: {ram}")
                else:
                    print(f"\n{Fore.YELLOW}No value entered")
                
                input(f"\n{Fore.YELLOW}Press ENTER to continue...")
                
            elif default_choice == "2":
                print(f"\n{Fore.YELLOW}Select default difficulty:")
                print(f"{THEME_COLOR}1. Peaceful")
                print(f"{THEME_COLOR}2. Easy")
                print(f"{THEME_COLOR}3. Normal")
                print(f"{THEME_COLOR}4. Hard")
                
                diff_choice = input(f"\n{THEME_COLOR}» {Fore.WHITE}").strip()
                
                difficulties = {"1": "peaceful", "2": "easy", "3": "normal", "4": "hard"}
                
                if diff_choice in difficulties:
                    settings['default_difficulty'] = difficulties[diff_choice]
                    save_settings(settings)
                    print(f"\n{Fore.GREEN}✔ Default difficulty set to: {difficulties[diff_choice].capitalize()}")
                else:
                    print(f"\n{Fore.RED}❌ Invalid choice")
                
                input(f"\n{Fore.YELLOW}Press ENTER to continue...")
            
        elif choice == "7":
            # Reset to defaults
            clear_screen()
            print_header("Reset Settings")
            
            confirm = input(f"\n{Fore.RED}⚠️  Reset all settings to defaults? (yes/no): {Fore.WHITE}")
            
            if confirm.lower() == 'yes':
                from settings_module import DEFAULT_SETTINGS
                settings = DEFAULT_SETTINGS.copy()
                save_settings(settings)
                THEME_COLOR = get_theme_color(settings['theme'])
                
                print(f"\n{Fore.GREEN}✔ Settings reset to defaults")
            else:
                print(f"\n{Fore.YELLOW}Reset cancelled")
            
            input(f"\n{Fore.YELLOW}Press ENTER to continue...")

def main_menu():
    """Main menu"""
    if settings.get('show_splash', True):
        splash()
    
    while True:
        clear_screen()
        print_header("PyCraftHub - Main Menu")
        
        data = load_data()
        total_servers = len(data) if data else 0
        running_servers = sum(1 for name in (data or {}) if is_server_running(name))
        
        print(f"\n{THEME_COLOR}╭─ Statistics " + "─" * 62 + "╮")
        print(f"{THEME_COLOR}│ {Fore.WHITE}Total Servers: {Fore.YELLOW}{total_servers:<10} "
              f"{Fore.WHITE}Running: {Fore.GREEN}{running_servers}/{total_servers:<20}{THEME_COLOR}│")
        print(f"{THEME_COLOR}╰" + "─" * 75 + "╯")
        
        print(f"\n{THEME_COLOR}╭─ Menu Options " + "─" * 60 + "╮")
        print(f"{THEME_COLOR}│                                                                        │")
        print(f"{THEME_COLOR}│  {Fore.GREEN}1.{Fore.WHITE} 🆕 Create New Server          {Fore.GREEN}2.{Fore.WHITE} 📝 Edit Server            {THEME_COLOR}│")
        print(f"{THEME_COLOR}│  {Fore.GREEN}3.{Fore.WHITE} 🎮 Manage Servers             {Fore.GREEN}4.{Fore.WHITE} 📋 View All Servers       {THEME_COLOR}│")
        print(f"{THEME_COLOR}│  {Fore.GREEN}5.{Fore.WHITE} 📦 List Mods/Plugins          {Fore.GREEN}6.{Fore.WHITE} 🔧 Server Tools           {THEME_COLOR}│")
        print(f"{THEME_COLOR}│  {Fore.GREEN}7.{Fore.WHITE} ℹ️  About PyCraftHub           {Fore.GREEN}8.{Fore.WHITE} 📖 Documentation          {THEME_COLOR}│")
        print(f"{THEME_COLOR}│  {Fore.GREEN}9.{Fore.WHITE} ⚙️  Settings                  {Fore.GREEN}0.{Fore.WHITE} 🚪 Exit                   {THEME_COLOR}│")
        print(f"{THEME_COLOR}│                                                                        │")
        print(f"{THEME_COLOR}╰" + "─" * 75 + "╯")
        
        choice = input(f"\n{THEME_COLOR}» {Fore.WHITE}").strip()
        
        if choice == "1":
            clear_screen()
            print_header("Create New Server")
            create_server()
            input(f"\n{Fore.GREEN}Press ENTER to continue...")
            
        elif choice == "2":
            clear_screen()
            print_header("Edit Server")
            edit_server()
            input(f"\n{Fore.GREEN}Press ENTER to continue...")
            
        elif choice == "3":
            server_management_menu()
            
        elif choice == "4":
            clear_screen()
            print_header("All Servers")
            list_servers()
            input(f"\n{Fore.GREEN}Press ENTER to continue...")
            
        elif choice == "5":
            clear_screen()
            print_header("List Mods/Plugins")
            server = input(f"\n{Fore.YELLOW}Server name: {Fore.WHITE}").strip()
            list_installed_mods(server)
            input(f"\n{Fore.GREEN}Press ENTER to continue...")
            
        elif choice == "6":
            server_tools_menu()
            
        elif choice == "7":
            show_about()
            
        elif choice == "8":
            show_documentation()
            
        elif choice == "9":
            settings_menu()
            
        elif choice == "0":
            clear_screen()
            print(f"\n{THEME_COLOR}╔" + "═" * 50 + "╗")
            print(f"{THEME_COLOR}║{Fore.YELLOW}  Thanks for using PyCraftHub!                    {THEME_COLOR}║")
            print(f"{THEME_COLOR}║{Fore.WHITE}  Created with ❤️  by Saransh                     {THEME_COLOR}║")
            print(f"{THEME_COLOR}╚" + "═" * 50 + "╝\n")
            break
            
        else:
            print(f"{Fore.RED}❌ Invalid option. Please try again.")
            input(f"\n{Fore.YELLOW}Press ENTER to continue...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        clear_screen()
        print(f"\n{Fore.YELLOW}Program interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress ENTER to exit...")
        sys.exit(1)
