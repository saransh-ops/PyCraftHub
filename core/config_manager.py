import json

DATA_FILE = "data/servers.json"

def configure_server():
    name = input("Server name: ")

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    if name not in data:
        print("❌ Server not found")
        return

    ram = input("RAM (e.g. 2G or 1024M): ")
    port = input("Port (default 25565): ")

    data[name]["ram"] = ram
    data[name]["port"] = int(port)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print("✔ Server updated")
