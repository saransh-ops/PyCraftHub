import psutil
import time
import sys
import os
from datetime import datetime

# Try to import colorama for colors
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class Fore:
        GREEN = YELLOW = RED = CYAN = WHITE = LIGHTBLACK_EX = LIGHTGREEN_EX = ""
    class Style:
        BRIGHT = RESET_ALL = ""

def clear_screen():
    """Clear console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_bar(percentage, length=20, full_char="█", empty_char="░"):
    """Create a visual progress bar"""
    filled = int(length * percentage / 100)
    empty = length - filled
    return full_char * filled + empty_char * empty

def get_color_for_percentage(percentage, reverse=False):
    """Get color based on percentage (green=good, red=bad)"""
    if not HAS_COLOR:
        return ""
    
    if reverse:  # For things where low is good (like CPU/RAM usage)
        if percentage < 50:
            return Fore.GREEN
        elif percentage < 75:
            return Fore.YELLOW
        else:
            return Fore.RED
    else:  # For things where high is good (like free space)
        if percentage > 50:
            return Fore.GREEN
        elif percentage > 25:
            return Fore.YELLOW
        else:
            return Fore.RED

def format_bytes(bytes_value):
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def get_uptime(start_time):
    """Calculate uptime"""
    elapsed = time.time() - start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python health_monitor.py <server_name>")
        sys.exit(1)
    
    server_name = sys.argv[1]
    server_path = f"servers/{server_name}"
    running_file = os.path.join(server_path, "running.txt")
    
    # Startup banner
    clear_screen()
    print(f"{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════════════════════════╗")
    print(f"{Fore.CYAN}║        PyCraftHub Health Monitor v3.0                  ║")
    print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}🔍 Monitoring: {Fore.WHITE}{server_name}")
    print(f"{Fore.YELLOW}📊 Updates every 2 seconds")
    print(f"{Fore.LIGHTBLACK_EX}Press Ctrl+C to stop monitoring\n")
    
    time.sleep(2)
    
    start_time = time.time()
    update_count = 0
    
    # Store history for trends
    cpu_history = []
    ram_history = []
    max_history = 10
    
    try:
        while True:
            # Check if server is still running
            if not os.path.exists(running_file):
                print(f"\n{Fore.YELLOW}⚠️  Server stopped - Health monitor closing...")
                time.sleep(1)
                break
            
            # Clear screen for update
            clear_screen()
            
            # Header
            print(f"{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════════════════════════╗")
            print(f"{Fore.CYAN}║  {Fore.WHITE}PyCraftHub Health Monitor v3.0{Fore.CYAN}                        ║")
            print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
            
            # Server info
            current_time = datetime.now().strftime("%H:%M:%S")
            uptime = get_uptime(start_time)
            
            print(f"\n{Fore.CYAN}┌─ Server Information " + "─" * 37 + "┐")
            print(f"{Fore.CYAN}│ {Fore.YELLOW}Server:{Fore.WHITE} {server_name:<46}{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ {Fore.YELLOW}Time:{Fore.WHITE} {current_time:<15} {Fore.YELLOW}Uptime:{Fore.WHITE} {uptime:<23}{Fore.CYAN}│")
            print(f"{Fore.CYAN}│ {Fore.YELLOW}Updates:{Fore.WHITE} {update_count:<44}{Fore.CYAN}│")
            print(f"{Fore.CYAN}└" + "─" * 58 + "┘")
            
            # Get system stats
            cpu_percent = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            ram_percent = ram.percent
            ram_used = format_bytes(ram.used)
            ram_total = format_bytes(ram.total)
            
            # Update history
            cpu_history.append(cpu_percent)
            ram_history.append(ram_percent)
            if len(cpu_history) > max_history:
                cpu_history.pop(0)
            if len(ram_history) > max_history:
                ram_history.pop(0)
            
            # CPU Section
            cpu_color = get_color_for_percentage(cpu_percent, reverse=True)
            cpu_bar = get_bar(cpu_percent, 30)
            
            print(f"\n{Fore.CYAN}┌─ CPU Usage " + "─" * 45 + "┐")
            print(f"{Fore.CYAN}│ {cpu_color}{cpu_bar} {cpu_percent:5.1f}%{Fore.CYAN}        │")
            
            # CPU cores
            try:
                cpu_per_core = psutil.cpu_percent(percpu=True)
                cores_display = "  ".join([f"{c:4.0f}%" for c in cpu_per_core[:4]])  # Show first 4 cores
                print(f"{Fore.CYAN}│ {Fore.LIGHTBLACK_EX}Cores: {cores_display:<44}{Fore.CYAN}│")
            except:
                pass
            
            # CPU trend (sparkline)
            if len(cpu_history) > 1:
                trend = "".join(["▁▂▃▄▅▆▇█"[min(7, int(c/12.5))] for c in cpu_history])
                print(f"{Fore.CYAN}│ {Fore.LIGHTBLACK_EX}Trend: {cpu_color}{trend:<44}{Fore.CYAN}│")
            
            print(f"{Fore.CYAN}└" + "─" * 58 + "┘")
            
            # RAM Section
            ram_color = get_color_for_percentage(ram_percent, reverse=True)
            ram_bar = get_bar(ram_percent, 30)
            
            print(f"\n{Fore.CYAN}┌─ RAM Usage " + "─" * 45 + "┐")
            print(f"{Fore.CYAN}│ {ram_color}{ram_bar} {ram_percent:5.1f}%{Fore.CYAN}        │")
            print(f"{Fore.CYAN}│ {Fore.LIGHTBLACK_EX}Used: {Fore.WHITE}{ram_used:<15} {Fore.LIGHTBLACK_EX}Total: {Fore.WHITE}{ram_total:<19}{Fore.CYAN}│")
            
            # RAM trend
            if len(ram_history) > 1:
                trend = "".join(["▁▂▃▄▅▆▇█"[min(7, int(r/12.5))] for r in ram_history])
                print(f"{Fore.CYAN}│ {Fore.LIGHTBLACK_EX}Trend: {ram_color}{trend:<44}{Fore.CYAN}│")
            
            print(f"{Fore.CYAN}└" + "─" * 58 + "┘")
            
            # Disk I/O (if available)
            try:
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
                disk_free = format_bytes(disk.free)
                disk_total = format_bytes(disk.total)
                disk_color = get_color_for_percentage(100 - disk_percent, reverse=True)
                disk_bar = get_bar(disk_percent, 30)
                
                print(f"\n{Fore.CYAN}┌─ Disk Usage " + "─" * 44 + "┐")
                print(f"{Fore.CYAN}│ {disk_color}{disk_bar} {disk_percent:5.1f}%{Fore.CYAN}        │")
                print(f"{Fore.CYAN}│ {Fore.LIGHTBLACK_EX}Free: {Fore.WHITE}{disk_free:<15} {Fore.LIGHTBLACK_EX}Total: {Fore.WHITE}{disk_total:<19}{Fore.CYAN}│")
                print(f"{Fore.CYAN}└" + "─" * 58 + "┘")
            except:
                pass
            
            # Network (if available)
            try:
                net = psutil.net_io_counters()
                sent = format_bytes(net.bytes_sent)
                recv = format_bytes(net.bytes_recv)
                
                print(f"\n{Fore.CYAN}┌─ Network " + "─" * 47 + "┐")
                print(f"{Fore.CYAN}│ {Fore.LIGHTBLACK_EX}Sent: {Fore.WHITE}{sent:<15} {Fore.LIGHTBLACK_EX}Received: {Fore.WHITE}{recv:<19}{Fore.CYAN}│")
                print(f"{Fore.CYAN}└" + "─" * 58 + "┘")
            except:
                pass
            
            # Status indicators
            print(f"\n{Fore.CYAN}┌─ Status " + "─" * 48 + "┐")
            
            # CPU status
            if cpu_percent < 50:
                cpu_status = f"{Fore.GREEN}● Healthy{Fore.WHITE}"
            elif cpu_percent < 75:
                cpu_status = f"{Fore.YELLOW}● Moderate{Fore.WHITE}"
            else:
                cpu_status = f"{Fore.RED}● High Load{Fore.WHITE}"
            
            # RAM status
            if ram_percent < 70:
                ram_status = f"{Fore.GREEN}● Healthy{Fore.WHITE}"
            elif ram_percent < 85:
                ram_status = f"{Fore.YELLOW}● Moderate{Fore.WHITE}"
            else:
                ram_status = f"{Fore.RED}● High Usage{Fore.WHITE}"
            
            print(f"{Fore.CYAN}│ {Fore.LIGHTBLACK_EX}CPU: {cpu_status:<40}{Fore.CYAN}    │")
            print(f"{Fore.CYAN}│ {Fore.LIGHTBLACK_EX}RAM: {ram_status:<40}{Fore.CYAN}    │")
            print(f"{Fore.CYAN}└" + "─" * 58 + "┘")
            
            # Footer
            print(f"\n{Fore.LIGHTBLACK_EX}Next update in 2 seconds... (Ctrl+C to stop)")
            
            update_count += 1
            time.sleep(2)
            
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⛔ Monitoring stopped by user")
    
    print(f"\n{Fore.CYAN}╔══════════════════════════════════════════════════════════╗")
    print(f"{Fore.CYAN}║  {Fore.GREEN}Monitoring session ended{Fore.CYAN}                              ║")
    print(f"{Fore.CYAN}║  {Fore.WHITE}Total updates: {update_count:<8}                             {Fore.CYAN}║")
    print(f"{Fore.CYAN}║  {Fore.WHITE}Session duration: {uptime:<8}                        {Fore.CYAN}║")
    print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}Closing in 2 seconds...")
    time.sleep(2)

if __name__ == "__main__":
    main()
