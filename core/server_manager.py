import os
import json
import shutil
import subprocess
import requests
import socket
import time
import psutil
import webbrowser
from pathlib import Path

DATA_FILE = os.path.join("data", "servers.json")




# -------------------- Utility Functions --------------------

server_processes = {}  # Tracks running server processes

def install_plugin(plugin_key, plugins_dir):
    plugin = PLUGIN_MAP[plugin_key]
    jar_path = plugins_dir / plugin["jar"]

    plugins_dir.mkdir(exist_ok=True)

    if jar_path.exists():
        print(f"✔ {plugin_key.capitalize()} already installed")
        return

    print(f"⬇ Installing {plugin_key.capitalize()}...")
    try:
        r = requests.get(plugin["download"], timeout=30)
        r.raise_for_status()

        with open(jar_path, "wb") as f:
            f.write(r.content)

        print(f"✔ {plugin_key.capitalize()} installed successfully")
    except Exception as e:
        print(f"❌ Failed to install {plugin_key}: {e}")

def remove_plugin(plugin_key, plugins_dir):
    plugin = PLUGIN_MAP[plugin_key]

    jar_path = plugins_dir / plugin["jar"]
    folder_path = plugins_dir / plugin["folder"]

    if jar_path.exists():
        jar_path.unlink()
        print(f"🗑 Deleted {plugin['jar']}")

    if folder_path.exists() and folder_path.is_dir():
        shutil.rmtree(folder_path)
        print(f"🗑 Deleted folder {plugin['folder']}")


def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_free_port():
    s = socket.socket()
    s.bind(('',0))
    port = s.getsockname()[1]
    s.close()
    return port

def select_ram():
    while True:
        total_ram_gb = psutil.virtual_memory().total / (1024**3)
        free_ram_gb = psutil.virtual_memory().available / (1024**3)
        print(f"\n🖥 Total RAM: {total_ram_gb:.1f} GB | Free RAM available: {free_ram_gb:.1f} GB")
        
        ram_input = input("Enter RAM for server (e.g., 2G, 4096M): ").strip().upper()
        if ram_input.endswith("G"):
            try:
                ram_gb = float(ram_input[:-1])
            except:
                print("❌ Invalid number")
                continue
        elif ram_input.endswith("M"):
            try:
                ram_gb = float(ram_input[:-1]) / 1024
            except:
                print("❌ Invalid number")
                continue
        else:
            print("❌ Please specify RAM in G or M (e.g., 2G, 2048M)")
            continue

        if ram_gb > free_ram_gb:
            print(f"❌ Not enough free RAM! Available: {free_ram_gb:.1f} GB. Try less.")
            continue

        print(f"✔ Allocating {ram_input} RAM for server\n")
        return ram_input


def ask_description():
    return input("Enter server description: ").strip()

def ask_render_distance():
    rd = input("Enter render distance (e.g., 8,10,12): ").strip()
    return int(rd) if rd.isdigit() else 10

def ask_difficulty():
    mapping = {"1": "peaceful", "2": "easy", "3": "normal", "4": "hard", "5": "hardcore"}
    while True:
        print("\nSelect difficulty:")
        print("1. Peaceful\n2. Easy\n3. Normal\n4. Hard\n5. Hardcore")
        choice = input("Choice: ").strip()
        if choice in mapping:
            return mapping[choice]
        print("❌ Invalid choice, try again.")

def is_playit_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and "playit" in proc.info['name'].lower():
            return True
    return False

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# -------------------- Plugin Installer --------------------

def install_recommended_fabric_mods(server_name, mc_version):
    mods = {
        "1": ("sodium", "performance"),
        "2": ("lithium", "performance"),
        "3": ("ferrite-core", "performance"),
        "4": ("simple-voice-chat", "Simple Voice Chat"),
    }

    print("\nSelect Fabric mods to install (comma-separated):")
    for k, (mod, _) in mods.items():
        print(f"{k}. {mod}")

    choice = input("> ").strip()
    if not choice:
        print("❌ No mods selected")
        return

    mods_dir = f"servers/{server_name}/mods"

    for c in choice.split(","):
        c = c.strip()
        if c in mods:
            project_id, _ = mods[c]
            download_modrinth_plugin(
                project_id,
                mc_version,
                "fabric",
                mods_dir
            )
        else:
            print(f"⚠ Invalid option: {c}")


def download_fabric(version, path):
    print(f"⬇ Downloading Fabric server {version}...")

    # Get latest fabric loader
    loader_meta = requests.get(
        "https://meta.fabricmc.net/v2/versions/loader"
    ).json()
    loader_version = loader_meta[0]["version"]

    # Get installer version
    installer_meta = requests.get(
        "https://meta.fabricmc.net/v2/versions/installer"
    ).json()
    installer_version = installer_meta[0]["version"]

    url = (
        f"https://meta.fabricmc.net/v2/versions/loader/"
        f"{version}/{loader_version}/{installer_version}/server/jar"
    )

    r = requests.get(url, stream=True)
    r.raise_for_status()

    jar_path = Path(path) / "fabric-server-launch.jar"
    with open(jar_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    print("✔ Fabric server downloaded")

def setup_fabric_dirs(server_dir):
    mods_dir = Path(server_dir) / "mods"
    mods_dir.mkdir(parents=True, exist_ok=True)


def install_fabric_api(version, mods_dir):
    print("⬇ Installing Fabric API...")

    url = "https://api.modrinth.com/v2/project/P7dR8mSH/version"
    versions = requests.get(url).json()

    for v in versions:
        if version in v["game_versions"] and "fabric" in v["loaders"]:
            file = v["files"][0]
            download_url = file["url"]

            path = Path(mods_dir) / file["filename"]
            r = requests.get(download_url, stream=True)

            with open(path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)

            print("✔ Fabric API installed")
            return

    print("⚠ No compatible Fabric API found")



def download_modrinth_plugin(
    project_slug,
    version,
    loader,
    plugins_dir
):
    os.makedirs(plugins_dir, exist_ok=True)

    api_url = (
        "https://api.modrinth.com/v2/project/"
        f"{project_slug}/version"
        f"?loaders=[\"{loader}\"]"
        f"&game_versions=[\"{version}\"]"
    )

    r = requests.get(api_url, timeout=15)
    if r.status_code != 200 or not r.json():
        print(f"❌ No compatible version found for {project_slug}")
        return

    version = r.json()[0]
    file = version["files"][0]

    download_url = file["url"]
    filename = file["filename"]

    path = os.path.join(plugins_dir, filename)

    print(f"⬇ Downloading {filename}...")
    with requests.get(download_url, stream=True) as d:
        d.raise_for_status()
        with open(path, "wb") as f:
            for chunk in d.iter_content(8192):
                f.write(chunk)

    print(f"✔ Installed {filename}")






def download_plugin_from_url(url, server_name, filename):
    plugins_dir = f"servers/{server_name}/plugins"
    os.makedirs(plugins_dir, exist_ok=True)

    print(f"⬇ Downloading {filename}...")
    r = requests.get(url, stream=True, timeout=30)
    r.raise_for_status()

    path = os.path.join(plugins_dir, filename)
    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    print(f"✔ Installed {filename}")



def create_server():
    name = input("Server name: ").strip()
    path = f"servers/{name}"

    if os.path.exists(path):
        print("❌ Server already exists")
        return

    # ---------------- SERVER TYPE ----------------
    print("Select server type:")
    print("1. Paper")
    print("2. Vanilla")
    print("3. Fabric")

    jar_type = {"1": "paper", "2": "vanilla", "3": "fabric"}.get(input("> ").strip())
    if not jar_type:
        print("❌ Invalid choice")
        return

    # ---------------- BASIC OPTIONS ----------------
    ram = select_ram()
    description = ask_description()
    render_distance = ask_render_distance()
    difficulty = ask_difficulty()

    hardcore = difficulty == "hardcore"
    if hardcore:
        difficulty = "hard"

    

    version = input("Enter Minecraft version (e.g., 1.21.4): ").strip()

    # ---------------- CREATE FOLDERS ----------------
    os.makedirs(path)
    os.makedirs(f"{path}/logs")
    os.makedirs(f"{path}/plugins")
    os.makedirs(f"{path}/mods", exist_ok=True)


    # ---------------- DOWNLOAD SERVER JAR ----------------
    try:
        if jar_type == "paper":
            download_paper(version, path)
        elif jar_type == "vanilla":
            download_vanilla(version, path)
        elif jar_type == "fabric":
            download_fabric(version, path)
            setup_fabric_dirs(path)
            if input("Install Fabric API? (y/n): ").strip().lower() == "y":
                install_fabric_api(version, f"{path}/mods")
            if input("Install recommended Fabric mods? (y/n):").strip().lower() == "y":
                install_recommended_fabric_mods(name, version)

    except Exception as e:
        print(f"❌ Failed to download server: {e}")
        shutil.rmtree(path)
        return

    # ---------------- ACCEPT EULA ----------------
    with open(f"{path}/eula.txt", "w") as f:
        f.write("eula=true")

    # ---------------- SAVE SERVER CONFIG (IMPORTANT) ----------------
    data = load_data()
    port = get_free_port()

    data[name] = {
        "ram": ram,
        "jar": "fabric-server-launch.jar" if jar_type == "fabric" else "server.jar",
        "port": port,
        "type": jar_type,
        "description": description,
        "render_distance": render_distance,
        "difficulty": difficulty,
        "hardcore": hardcore,
        "version": version
    }

    save_data(data)  # 🔥 MUST happen BEFORE plugins

    # ---------------- server.properties ----------------
    with open(f"{path}/server.properties", "w") as f:
        f.write(f"server-port={port}\n")
        f.write("online-mode=true\n")
        f.write(f"render-distance={render_distance}\n")
        f.write(f"view-distance={render_distance}\n")
        f.write(f"difficulty={difficulty}\n")
        if hardcore:
            f.write("hardcore=true\n")

    # ---------------- PAPER EXTRAS ----------------
    if jar_type == "paper":

        if input("Install Geyser for Bedrock? (y/n): ").strip().lower() == "y":
            install_geyser(name)

        if input("Install recommended plugins? (y/n): ").strip().lower() == "y":
            install_recommended_plugins(name,version)



    # ---------------- DONE ----------------
    print(f"\n✔ {jar_type.upper()} server '{name}' created successfully!")
    print(f"🖥 Local join address: {get_local_ip()}:{port}")


RECOMMENDED_PLUGINS = {
    "1": ("ViaVersion", "viaversion"),
    "2": ("ViaBackwards", "viabackwards"),
    "3": ("ViaRewind", "viarewind"),
    "4": ("EssentialsX", "essentialsx"),
    "5": ("SkinRestorer", "skinsrestorer"),
    "6": ("Chunky", "chunky"),
}


def install_recommended_plugins(server_name, mc_version):

    server_data = load_data().get(server_name)
    if server_data["type"] != "paper":
        print("⚠ Plugins are only supported on Paper servers")
        return

    
    plugins_dir = f"servers/{server_name}/plugins"

    print("\nSelect plugins to install (comma-separated):")
    for k, (name, _) in RECOMMENDED_PLUGINS.items():
        print(f"{k}. {name}")

    choice = input("> ").strip()
    if not choice:
        print("❌ No plugins selected")
        return

    for c in choice.split(","):
        c = c.strip()
        if c in RECOMMENDED_PLUGINS:
            name, slug = RECOMMENDED_PLUGINS[c]
            download_modrinth_plugin(
                slug,
                mc_version,
                "paper",
                plugins_dir
            )
        else:
            print(f"⚠ Invalid option: {c}")






# URLs for the latest builds
GEYSER_URL = "https://download.geysermc.org/v2/projects/geyser/versions/latest/builds/latest/downloads/spigot"
FLOODGATE_URL = "https://download.geysermc.org/v2/projects/floodgate/versions/latest/builds/latest/downloads/spigot"

def install_geyser(server_name, bedrock_port="19132"):
    """
    Fully automated Geyser + Floodgate installer for a Paper server.
    
    Args:
        server_name: Name of your server folder inside 'servers/'
        bedrock_port: Port for Bedrock clients to connect
    """
    server_path = f"servers/{server_name}"
    plugins_path = os.path.join(server_path, "plugins")
    os.makedirs(plugins_path, exist_ok=True)

    # Download Geyser
    print(f"⬇ Downloading Geyser-Spigot for {server_name}...")
    r = requests.get(GEYSER_URL)
    geyser_file = os.path.join(plugins_path, "Geyser-Spigot.jar")
    with open(geyser_file, "wb") as f:
        f.write(r.content)

    # Download Floodgate
    print(f"⬇ Downloading Floodgate-Spigot for {server_name}...")
    r = requests.get(FLOODGATE_URL)
    floodgate_file = os.path.join(plugins_path, "Floodgate-Spigot.jar")
    with open(floodgate_file, "wb") as f:
        f.write(r.content)

    # Create basic Geyser config.yml
    config_path = os.path.join(plugins_path, "Geyser-Spigot", "config.yml")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    config_content = f"""bedrock:
  address: 0.0.0.0
  port: {bedrock_port}

remote:
  address: 127.0.0.1
  port: 25565

floodgate-key-file: plugins/Floodgate/key.pem
"""
    with open(config_path, "w") as f:
        f.write(config_content)

    print(f"✔ Geyser + Floodgate installed for '{server_name}'")
    print(f"⚠ Make sure to create a UDP tunnel for Bedrock port {bedrock_port} in Playit.gg")

# -------------------- Server Functions --------------------

def list_servers():
    data = load_data()
    if not data:
        print("❌ No servers found")
        return
    print("\nAvailable servers:")
    for name, info in data.items():
        status = "Running" if name in server_processes else "Stopped"
        print(f"- {name} | Type: {info['type']} | Port: {info['port']} | Status: {status}")

def download_paper(version, path):
    print(f"⬇ Downloading PaperMC {version}...")

    api_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}"
    r = requests.get(api_url, timeout=15)

    if r.status_code != 200:
        raise RuntimeError(f"PaperMC version '{version}' not found")

    data = r.json()
    builds = data.get("builds")

    if not builds:
        raise RuntimeError("No Paper builds found")

    build = max(builds)  # ✅ FIX HERE

    jar_url = (
        f"https://api.papermc.io/v2/projects/paper/versions/"
        f"{version}/builds/{build}/downloads/paper-{version}-{build}.jar"
    )

    jar_path = os.path.join(path, "server.jar")

    with requests.get(jar_url, stream=True, timeout=30) as r2:
        r2.raise_for_status()
        with open(jar_path, "wb") as f:
            for chunk in r2.iter_content(8192):
                f.write(chunk)

    if os.path.getsize(jar_path) < 10 * 1024 * 1024:
        raise RuntimeError("Downloaded Paper jar is corrupt")

    print(f"✔ Paper {version} (build {build}) downloaded")




def download_vanilla(version, server_path):
    print(f"⬇ Downloading Vanilla {version}...")

    manifest = requests.get(
        "https://launchermeta.mojang.com/mc/game/version_manifest.json"
    ).json()

    version_data = next((v for v in manifest["versions"] if v["id"] == version), None)
    if not version_data:
        raise Exception("❌ Invalid Minecraft version")

    version_json = requests.get(version_data["url"]).json()
    jar_url = version_json["downloads"]["server"]["url"]

    jar_path = os.path.join(server_path, "server.jar")
    r = requests.get(jar_url)

    with open(jar_path, "wb") as f:
        f.write(r.content)

    print("✔ Vanilla server downloaded")

def download_fabric(version, server_path):
    print(f"⬇ Downloading Fabric {version}...")

    loader = requests.get(
        "https://meta.fabricmc.net/v2/versions/loader"
    ).json()[0]["version"]

    installer_url = "https://meta.fabricmc.net/v2/versions/installer"
    installer = requests.get(installer_url).json()[0]["version"]

    fabric_jar_url = (
        f"https://meta.fabricmc.net/v2/versions/loader/"
        f"{version}/{loader}/{installer}/server/jar"
    )

    jar_path = os.path.join(server_path, "server.jar")
    r = requests.get(fabric_jar_url)

    if r.status_code != 200:
        raise Exception("❌ Failed to download Fabric")

    with open(jar_path, "wb") as f:
        f.write(r.content)

    print("✔ Fabric server downloaded")





def edit_server():
    server_name = input("Enter server name to edit: ").strip()
    server_path = Path("servers") / server_name
    config_path = server_path / "server.json"

    if not server_path.exists() or not config_path.exists():
        print("❌ Server not found")
        return

    with open(config_path, "r") as f:
        server = json.load(f)

    # =========================
    # SAVE OLD STATES
    # =========================
    old_jar_type = server.get("jar_type")
    old_version = server.get("version")
    old_difficulty = server.get("difficulty")

    for key in ["lifesteal", "headsteal"]:
        server[f"_old_{key}"] = server.get(key, False)

    plugins_dir = server_path / "plugins"

    # =========================
    # EDIT MENU
    # =========================
    print("\n--- Edit Server ---")
    print("1. Change server software (Paper / Vanilla / Fabric)")
    print("2. Change Minecraft version")
    print("3. Change difficulty")
    print("4. Toggle Lifesteal")
    print("5. Toggle Headsteal")
    print("6. Save & Exit")
    print("7. Cancel")

    choice = input("Choose option: ").strip()

    # =========================
    # 1️⃣ CHANGE SERVER SOFTWARE
    # =========================
    if choice == "1":
        print("\nSelect server software:")
        print("1. Paper")
        print("2. Vanilla")
        print("3. Fabric")

        s = input("Choice: ").strip()

        if s == "1":
            server["jar_type"] = "paper"
        elif s == "2":
            server["jar_type"] = "vanilla"
        elif s == "3":
            server["jar_type"] = "fabric"
        else:
            print("❌ Invalid choice")
            return

        print(f"✔ Selected {server['jar_type'].capitalize()}")

    # =========================
    # 2️⃣ CHANGE VERSION
    # =========================
    elif choice == "2":
        server["version"] = input(
            f"Enter version (current {server['version']}): "
        ).strip()

    # =========================
    # 3️⃣ CHANGE DIFFICULTY
    # =========================
    elif choice == "3":
        print("\nSelect difficulty:")
        print("1. peaceful")
        print("2. easy")
        print("3. normal")
        print("4. hard")
        print("5. hardcore")

        d = input("Choice: ").strip()
        diff_map = {
            "1": "peaceful",
            "2": "easy",
            "3": "normal",
            "4": "hard",
            "5": "hardcore"
        }

        if d not in diff_map:
            print("❌ Invalid difficulty")
            return

        server["difficulty"] = diff_map[d]

    # =========================
    # 4️⃣ TOGGLE LIFESTEAL
    # =========================
    elif choice == "4":
        server["lifesteal"] = not server.get("lifesteal", False)
        print(f"Lifesteal set to {server['lifesteal']}")

    # =========================
    # 5️⃣ TOGGLE HEADSTEAL
    # =========================
    elif choice == "5":
        server["headsteal"] = not server.get("headsteal", False)
        print(f"Headsteal set to {server['headsteal']}")

    # =========================
    # SAVE & APPLY
    # =========================
    elif choice == "6":

        # -------------------------
        # RE-DOWNLOAD JAR IF NEEDED
        # -------------------------
        if (
            server["jar_type"] != old_jar_type
            or server["version"] != old_version
        ):
            print("🔁 Re-downloading server jar...")

            try:
                if server["jar_type"] == "paper":
                    download_paper(server["version"], server_path)
                elif server["jar_type"] == "vanilla":
                    download_vanilla(server["version"], server_path)
                elif server["jar_type"] == "fabric":
                    download_fabric(server["version"], server_path)

                print("✔ Server software updated")

            except Exception as e:
                print(f"❌ Failed to update server jar: {e}")
                return

        # -------------------------
        # APPLY LIFESTEAL / HEADSTEAL (REAL)
        # -------------------------
        if server["jar_type"] == "paper":
            handle_lifesteal(server_name, server.get("lifesteal", False))
            handle_headsteal(server_name, server.get("headsteal", False))
        else:
            # Auto-disable if not Paper
            server["lifesteal"] = False
            server["headsteal"] = False


        # -------------------------
        # SAVE CONFIG
        # -------------------------
        with open(config_path, "w") as f:
            json.dump(server, f, indent=4)

        # Cleanup temp keys
        server.pop("_old_lifesteal", None)
        server.pop("_old_headsteal", None)


        print("✔ Server updated successfully")
        return

    # =========================
    # CANCEL
    # =========================
    elif choice == "7":
        print("❌ Edit cancelled")
        return

    else:
        print("❌ Invalid option")


# -------------------- Server Management --------------------

def start_server(name):
    data = load_data()   # your existing function

    if name not in data:
        print("❌ Server not found")
        return

    server = data[name]
    path = f"servers/{name}"

    jar = server["jar"]
    ram = server["ram"]
    port = server["port"]

    jar_path = os.path.join(path, jar)
    if not os.path.exists(jar_path):
        print(f"❌ JAR file not found: {jar}")
        return

    if name in server_processes:
        print("❌ Server is already running")
        return

    print("\n▶ Starting Minecraft server...")
    print(f"⚙ RAM: {ram}")
    print(f"🔌 Port: {port}")

    process = subprocess.Popen(
        ["java", f"-Xms{ram}", f"-Xmx{ram}", "-jar", jar, "nogui"],
        cwd=path
    )

    server_processes[name] = process

    local_ip = get_local_ip()

    print("\n✔ Server started")
    print(f"🖥 Local join address: {local_ip}:{port}")

    # ---------- PLAYIT CHECK ----------
    if not is_playit_running():
        print("\n⚠ Playit.gg agent is NOT running")
        print("👉 Start playit.exe and login")
        print("👉 Then create a tunnel in the browser")
        return

    print("\n🔗 Playit.gg agent detected")
    print("🌐 Opening Playit dashboard...")

    webbrowser.open("https://playit.gg/account/agents")

    print("\n⚠ IMPORTANT:")
    print("If you do NOT see a tunnel for this port:")
    print(f"👉 Create a TCP tunnel for 127.0.0.1:{port}")
    print("👉 Select service: Minecraft Java")
    print("👉 Save once (only needed first time)")


def stop_server(name):
    process = server_processes.get(name)
    if not process:
        print("❌ Server is not running")
        return
    print(f"Stopping server '{name}'...")
    process.terminate()
    process.wait()
    del server_processes[name]
    print(f"✔ Server '{name}' stopped")

def restart_server(name):
    print(f"Restarting server '{name}'...")
    stop_server(name)
    time.sleep(2)
    start_server(name)
    print(f"✔ Server '{name}' restarted")

def delete_server(name):
    path = f"servers/{name}"
    if os.path.exists(path):
        if name in server_processes:
            stop_server(name)
        shutil.rmtree(path)
    data = load_data()
    if name in data:
        del data[name]
        save_data(data)
    print(f"✔ Server '{name}' deleted")
