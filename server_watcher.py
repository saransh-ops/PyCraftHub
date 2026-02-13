"""
ULTRA SIMPLE Server Watcher - Easy to debug
"""
import os
import sys
import time

print("="*60)
print("SERVER WATCHER STARTING")
print("="*60)

# Check arguments
if len(sys.argv) < 3:
    print("ERROR: Need 2 arguments!")
    print(f"Got: {sys.argv}")
    input("Press Enter to exit...")
    sys.exit(1)

server_name = sys.argv[1]
server_pid = sys.argv[2]

print(f"Server Name: {server_name}")
print(f"Server PID: {server_pid}")

# Setup paths
server_path = f"servers/{server_name}"
command_file = os.path.join(server_path, "command.txt")
running_file = os.path.join(server_path, "running.txt")

print(f"Command file: {command_file}")
print(f"Running file: {running_file}")

if not os.path.exists(server_path):
    print(f"ERROR: Server path doesn't exist: {server_path}")
    input("Press Enter to exit...")
    sys.exit(1)

print("✔ Server path exists")
print("\nWatching for stop command...")
print("(Press Ctrl+C to stop watcher)\n")

# Main loop
try:
    loop_count = 0
    while True:
        loop_count += 1
        
        # Show we're alive every 10 seconds
        if loop_count % 20 == 0:
            print(f"Still watching... (loop {loop_count})")
        
        # Check for stop command
        if os.path.exists(command_file):
            print("\n⚠ COMMAND FILE DETECTED!")
            
            try:
                with open(command_file, "r") as f:
                    cmd = f.read().strip()
                
                print(f"Command: '{cmd}'")
                
                if cmd.lower() == "stop":
                    print("⛔ STOP COMMAND RECEIVED!")
                    print(f"Killing process {server_pid}...")
                    
                    # Use taskkill
                    result = os.system(f"taskkill /F /PID {server_pid} /T")
                    print(f"Taskkill result: {result}")
                    
                    # Wait a bit
                    time.sleep(2)
                    
                    # Clean up files
                    try:
                        if os.path.exists(running_file):
                            os.remove(running_file)
                            print("✔ Removed running.txt")
                    except:
                        pass
                    
                    try:
                        if os.path.exists(command_file):
                            os.remove(command_file)
                            print("✔ Removed command.txt")
                    except:
                        pass
                    
                    print("\n✔ SERVER STOPPED")
                    break
                    
            except Exception as e:
                print(f"ERROR reading command: {e}")
        
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n⛔ Watcher interrupted by user")

print("\nWatcher stopped. Closing in 2 seconds...")
time.sleep(2)
# Window closes automatically now - no input() prompt
