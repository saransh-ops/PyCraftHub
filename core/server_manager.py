try:
    from notifications import (
        notify_server_start, notify_server_stop,
        notify_server_created, notify_server_deleted
    )
except ImportError:
    def notify_server_start(*args, **kwargs): pass
    def notify_server_stop(*args, **kwargs): pass
    def notify_server_created(*args, **kwargs): pass
    def notify_server_deleted(*args, **kwargs): pass

import tkinter as tk
from tkinter import filedialog
import os
import json
import shutil
import subprocess
import requests
import socket
import time
import psutil
import webbrowser
import threading
from pathlib import Path

DATA_FILE = os.path.join("data", "servers.json")




# -------------------- Utility Functions --------------------

server_processes = {}  # Tracks running server processes

def select_folder(title):
    root = tk.Tk()
    root.withdraw()   # hide empty tkinter window
    root.attributes('-topmost', True)

    folder = filedialog.askdirectory(title=title)
    root.destroy()
    return folder


def import_world(server_name):
    server_path = f"servers/{server_name}"

    print("\n🌍 Import World")
    print("1. Import from Singleplayer")
    print("2. Import from Server")

    choice = input("> ").strip()

    # ---------- SINGLEPLAYER ----------
    if choice == "1":
        print("\n📂 Select SINGLEPLAYER world folder")
        src = select_folder("Select Singleplayer World Folder")

        if not src:
            print("❌ No folder selected")
            return

        dst = os.path.join(server_path, "world")

        if os.path.exists(dst):
            shutil.rmtree(dst)

        shutil.copytree(src, dst)
        print("✅ Singleplayer world imported")

    # ---------- SERVER ----------
    elif choice == "2":
        worlds = [
            ("world", "Select OVERWORLD folder"),
            ("world_nether", "Select NETHER folder"),
            ("world_the_end", "Select END folder")
        ]

        for folder, title in worlds:
            print(f"\n📂 {title}")
            src = select_folder(title)

            if not src:
                print("❌ Import cancelled")
                return

            dst = os.path.join(server_path, folder)

            if os.path.exists(dst):
                shutil.rmtree(dst)

            shutil.copytree(src, dst)
            print(f"✅ {folder} imported")

        print("\n🎉 Server world fully imported")

    else:
        print("❌ Invalid option")




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

def download_purpur(version, path):
    """Download Purpur server jar"""
    print(f"⬇ Downloading Purpur {version}...")
    
    try:
        # Get latest Purpur build for this version
        api_url = f"https://api.purpurmc.org/v2/purpur/{version}"
        r = requests.get(api_url, timeout=15)
        
        if r.status_code != 200:
            raise RuntimeError(f"Purpur version '{version}' not found")
        
        data = r.json()
        builds = data.get("builds")
        
        if not builds or not builds.get("latest"):
            raise RuntimeError("No Purpur builds found")
        
        latest_build = builds["latest"]
        
        # Download the jar
        jar_url = f"https://api.purpurmc.org/v2/purpur/{version}/{latest_build}/download"
        
        jar_path = os.path.join(path, "server.jar")
        
        with requests.get(jar_url, stream=True, timeout=30) as r2:
            r2.raise_for_status()
            with open(jar_path, "wb") as f:
                for chunk in r2.iter_content(8192):
                    f.write(chunk)
        
        if os.path.getsize(jar_path) < 10 * 1024 * 1024:
            raise RuntimeError("Downloaded Purpur jar is corrupt")
        
        print(f"✔ Purpur {version} (build {latest_build}) downloaded")
        
    except Exception as e:
        raise RuntimeError(f"Failed to download Purpur: {e}")


def install_recommended_purpur_plugins(server_name, mc_version):
    """Install recommended plugins for Purpur"""
    plugins_dir = f"servers/{server_name}/plugins"
    
    # Purpur uses same plugins as Paper/Spigot
    print("\nPurpur-compatible plugins (same as Paper):")
    print("1. ViaVersion")
    print("2. ViaBackwards")
    print("3. EssentialsX")
    print("4. LuckPerms")
    print("5. Vault")
    print("6. WorldEdit")
    
    choice = input("\nSelect plugins to install (comma-separated): ").strip()
    if not choice:
        print("❌ No plugins selected")
        return
    
    purpur_plugins = {
        "1": ("ViaVersion", "viaversion"),
        "2": ("ViaBackwards", "viabackwards"),
        "3": ("EssentialsX", "essentialsx"),
        "4": ("LuckPerms", "luckperms"),
        "5": ("Vault", "vault"),
        "6": ("WorldEdit", "worldedit")
    }
    
    for c in choice.split(","):
        c = c.strip()
        if c in purpur_plugins:
            name, slug = purpur_plugins[c]
            download_modrinth_plugin(
                slug,
                mc_version,
                "purpur",
                plugins_dir
            )
        else:
            print(f"⚠ Invalid option: {c}")


# ==================== FORGE SUPPORT ====================

def download_forge(version, path):
    """Download and AUTO-INSTALL Forge server"""
    print(f"⬇ Downloading Forge {version}...")
    
    try:
        # Get Forge version list
        forge_api = "https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json"
        r = requests.get(forge_api, timeout=15)
        
        if r.status_code != 200:
            raise RuntimeError("Could not connect to Forge API")
        
        promos = r.json()["promos"]
        
        # Try to find recommended version for this MC version
        forge_version = None
        
        # Check for recommended version
        rec_key = f"{version}-recommended"
        lat_key = f"{version}-latest"
        
        if rec_key in promos:
            forge_version = promos[rec_key]
        elif lat_key in promos:
            forge_version = promos[lat_key]
        else:
            print(f"⚠ No direct Forge version found for {version}")
            print("Trying to find latest compatible version...")
            
            # Try to find any version for this MC version
            for key in promos:
                if key.startswith(version):
                    forge_version = promos[key]
                    break
            
            if not forge_version:
                print(f"❌ No Forge version available for Minecraft {version}")
                print("\nPlease download Forge manually from:")
                print(f"https://files.minecraftforge.net/net/minecraftforge/forge/index_{version}.html")
                raise RuntimeError("Forge version not found")
        
        # Construct Forge installer URL
        forge_full = f"{version}-{forge_version}"
        installer_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{forge_full}/forge-{forge_full}-installer.jar"
        
        print(f"📥 Downloading Forge {forge_full} installer...")
        
        installer_path = os.path.join(path, "forge-installer.jar")
        
        with requests.get(installer_url, stream=True, timeout=60) as r2:
            r2.raise_for_status()
            
            # Download with progress
            total_size = int(r2.headers.get('content-length', 0))
            downloaded = 0
            
            with open(installer_path, "wb") as f:
                for chunk in r2.iter_content(8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        percent = (downloaded / total_size) * 100
                        print(f"\rDownloading... {percent:.1f}%", end='', flush=True)
            
            print()  # New line after progress
        
        print("✔ Forge installer downloaded")
        
        # ============ AUTO-INSTALL FORGE ============
        print("\n🔧 Installing Forge server (this may take 2-5 minutes)...")
        print("⏳ Please wait, do not close PyCraftHub...")
        
        abs_path = os.path.abspath(path)
        
        # Run the installer
        install_process = subprocess.Popen(
            ["java", "-jar", "forge-installer.jar", "--installServer"],
            cwd=abs_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Show progress while installing
        print("\nInstallation progress:")
        for line in install_process.stdout:
            line = line.strip()
            if line:
                # Filter out noise and show important messages
                if any(keyword in line.lower() for keyword in ['downloading', 'building', 'installing', 'complete']):
                    print(f"  {line}")
        
        # Wait for installation to complete
        install_process.wait()
        
        if install_process.returncode != 0:
            # Installation failed
            error_output = install_process.stderr.read()
            print(f"\n❌ Forge installation failed!")
            print(f"Error: {error_output}")
            raise RuntimeError("Forge installation failed")
        
        # Verify installation
        if not os.path.exists(os.path.join(abs_path, "libraries")):
            raise RuntimeError("Forge installation incomplete - libraries folder not found")
        
        # Check if run.bat was created
        if not os.path.exists(os.path.join(abs_path, "run.bat")):
            # Try to find the forge jar and create run.bat manually
            forge_jar = None
            for file in os.listdir(abs_path):
                if file.startswith("forge") and file.endswith(".jar") and "installer" not in file:
                    forge_jar = file
                    break
            
            if forge_jar:
                # Create run.bat manually
                with open(os.path.join(abs_path, "run.bat"), "w") as f:
                    f.write('@echo off\n')
                    f.write(f'java -jar {forge_jar} %*\n')
                print("✔ Created run.bat manually")
            else:
                raise RuntimeError("Could not find Forge server jar")
        
        print("\n✔ Forge server installed successfully!")
        print(f"✔ Server ready to start")
        
        # Clean up installer
        try:
            os.remove(installer_path)
            print("✔ Cleaned up installer")
        except:
            pass
        
    except Exception as e:
        raise RuntimeError(f"Failed to setup Forge: {e}")


# ============ ALTERNATIVE: Silent Installation ============

def download_forge_silent(version, path):
    """
    Silent Forge installation with minimal output
    Use this if you want less verbose installation
    """
    print(f"⬇ Downloading Forge {version}...")
    
    try:
        # Get Forge version
        forge_api = "https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json"
        r = requests.get(forge_api, timeout=15)
        
        if r.status_code != 200:
            raise RuntimeError("Could not connect to Forge API")
        
        promos = r.json()["promos"]
        
        rec_key = f"{version}-recommended"
        lat_key = f"{version}-latest"
        
        if rec_key in promos:
            forge_version = promos[rec_key]
        elif lat_key in promos:
            forge_version = promos[lat_key]
        else:
            raise RuntimeError(f"No Forge version for Minecraft {version}")
        
        forge_full = f"{version}-{forge_version}"
        installer_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{forge_full}/forge-{forge_full}-installer.jar"
        
        installer_path = os.path.join(path, "forge-installer.jar")
        
        # Download
        with requests.get(installer_url, stream=True, timeout=60) as r2:
            r2.raise_for_status()
            with open(installer_path, "wb") as f:
                for chunk in r2.iter_content(8192):
                    f.write(chunk)
        
        print("✔ Installer downloaded")
        
        # Install
        print("🔧 Installing Forge (please wait 2-5 minutes)...")
        
        abs_path = os.path.abspath(path)
        
        result = subprocess.run(
            ["java", "-jar", "forge-installer.jar", "--installServer"],
            cwd=abs_path,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Installation failed: {result.stderr}")
        
        # Verify
        if not os.path.exists(os.path.join(abs_path, "libraries")):
            raise RuntimeError("Installation incomplete")
        
        print("✔ Forge installed!")
        
        # Cleanup
        try:
            os.remove(installer_path)
        except:
            pass
            
    except subprocess.TimeoutExpired:
        raise RuntimeError("Installation timeout - took too long")
    except Exception as e:
        raise RuntimeError(f"Failed to setup Forge: {e}")


def setup_forge_dirs(server_dir):
    """Create Forge directory structure"""
    mods_dir = Path(server_dir) / "mods"
    config_dir = Path(server_dir) / "config"
    
    mods_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)


def install_recommended_forge_mods(server_name, mc_version):
    """Install recommended Forge mods"""
    mods_dir = f"servers/{server_name}/mods"
    
    print("\nRecommended Forge mods:")
    print("1. JEI (Just Enough Items)")
    print("2. JourneyMap")
    print("3. Biomes O' Plenty")
    print("4. Create")
    print("5. Applied Energistics 2")
    print("6. Tinkers' Construct")
    
    choice = input("\nSelect mods to install (comma-separated): ").strip()
    if not choice:
        print("❌ No mods selected")
        return
    
    forge_mods = {
        "1": ("JEI", "jei"),
        "2": ("JourneyMap", "journeymap"),
        "3": ("Biomes O' Plenty", "biomes-o-plenty"),
        "4": ("Create", "create"),
        "5": ("Applied Energistics 2", "applied-energistics-2"),
        "6": ("Tinkers' Construct", "tinkers-construct")
    }
    
    for c in choice.split(","):
        c = c.strip()
        if c in forge_mods:
            name, slug = forge_mods[c]
            download_modrinth_plugin(
                slug,
                mc_version,
                "forge",
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



def download_modrinth_plugin(project_slug, mc_version, loader, target_dir):
    os.makedirs(target_dir, exist_ok=True)

    api_url = (
        f"https://api.modrinth.com/v2/project/{project_slug}/version"
        f"?loaders=[\"{loader}\"]"
        f"&game_versions=[\"{mc_version}\"]"
    )

    r = requests.get(api_url, timeout=15)
    if r.status_code != 200 or not r.json():
        print(f"❌ No compatible version found for {project_slug}")
        return

    version_data = r.json()[0]
    file = version_data["files"][0]

    filename = file["filename"]
    download_url = file["url"]

    if is_already_installed(filename, target_dir):
        print(f"✔ {filename} already installed, skipping")
        return

    # ---------------- DOWNLOAD MAIN MOD ----------------
    print(f"⬇ Downloading {filename}...")
    with requests.get(download_url, stream=True) as d:
        d.raise_for_status()
        with open(os.path.join(target_dir, filename), "wb") as f:
            for chunk in d.iter_content(8192):
                f.write(chunk)

    print(f"✔ Installed {filename}")

    # ---------------- HANDLE DEPENDENCIES ----------------
    deps = version_data.get("dependencies", [])

    for dep in deps:
        if dep["dependency_type"] != "required":
            continue

        dep_id = dep.get("project_id")
        if not dep_id:
            continue

        # Skip Fabric API (you already handle it separately)
        if dep_id.lower() == "fabric-api":
            print("ℹ Fabric API dependency detected (skipped)")
            continue

        print(f"🔗 Required dependency detected: {dep_id}")

        dep_api = f"https://api.modrinth.com/v2/project/{dep_id}"
        dep_info = requests.get(dep_api).json()
        dep_slug = dep_info["slug"]

        download_modrinth_plugin(
            dep_slug,
            mc_version,
            loader,
            target_dir
        )



def get_installed_files(target_dir):
    if not os.path.exists(target_dir):
        return []
    return [f.lower() for f in os.listdir(target_dir) if f.endswith(".jar")]


def is_already_installed(filename, target_dir):
    return filename.lower() in get_installed_files(target_dir)


def list_installed_mods(server_name):
    data = load_data()
    server = data.get(server_name)

    if not server:
        print("❌ Server not found")
        return

    if server["type"] == "paper":
        target_dir = f"servers/{server_name}/plugins"
    elif server["type"] == "fabric":
        target_dir = f"servers/{server_name}/mods"
    else:
        print("⚠ Vanilla has no mods/plugins")
        return

    files = get_installed_files(target_dir)

    if not files:
        print("❌ No mods/plugins installed")
        return

    print("\n📦 Installed mods/plugins:")
    for f in files:
        print(f"- {f}")


def remove_mod_plugin(server_name):
    data = load_data()
    server = data.get(server_name)

    if server["type"] == "paper":
        target_dir = f"servers/{server_name}/plugins"
    elif server["type"] == "fabric":
        target_dir = f"servers/{server_name}/mods"
    else:
        return

    files = get_installed_files(target_dir)
    if not files:
        print("❌ Nothing to remove")
        return

    print("\nSelect mod/plugin to remove:")
    for i, f in enumerate(files, 1):
        print(f"{i}. {f}")

    choice = input("> ").strip()
    if not choice.isdigit():
        return

    index = int(choice) - 1
    if index >= len(files):
        return

    os.remove(os.path.join(target_dir, files[index]))
    print(f"🗑 Removed {files[index]}")


def update_mod_plugin(server_name):
    data = load_data()
    server = data.get(server_name)

    if server["type"] == "paper":
        target_dir = f"servers/{server_name}/plugins"
        loader = "paper"
    elif server["type"] == "fabric":
        target_dir = f"servers/{server_name}/mods"
        loader = "fabric"
    else:
        return

    files = get_installed_files(target_dir)
    if not files:
        print("❌ No mods/plugins installed")
        return

    print("\nSelect mod/plugin to update:")
    for i, f in enumerate(files, 1):
        print(f"{i}. {f}")

    choice = input("> ").strip()
    if not choice.isdigit():
        return

    index = int(choice) - 1
    if index >= len(files):
        return

    filename = files[index]
    slug_guess = filename.split("-")[0]

    os.remove(os.path.join(target_dir, filename))
    print("🔁 Updating...")

    download_modrinth_plugin(
        slug_guess,
        server["version"],
        loader,
        target_dir
    )


def search_modrinth(query, loader, mc_version):
    url = "https://api.modrinth.com/v2/search"
    params = {
        "query": query,
        "facets": (
            f'[["categories:{loader}"],["versions:{mc_version}"]]'
        ),
        "limit": 7
    }

    r = requests.get(url, params=params, timeout=15)
    if r.status_code != 200:
        return []

    return r.json().get("hits", [])


def mod_plugin_search_menu(server_name):
    data = load_data()
    server = data.get(server_name)

    if not server:
        print("❌ Server not found")
        return

    loader = server["type"]      # paper / fabric
    mc_version = server["version"]

    if loader == "paper":
        target_dir = f"servers/{server_name}/plugins"
    elif loader == "fabric":
        target_dir = f"servers/{server_name}/mods"
    else:
        print("⚠ Mods/plugins not supported on Vanilla")
        return

    while True:
        print("\n🔹 Mod / Plugin Search Menu")
        print("1. Search & install")
        print("2. Exit")

        main_choice = input("> ").strip()

        if main_choice == "2":
            print("✔ Finished installing mods/plugins")
            return

        if main_choice != "1":
            print("❌ Invalid option")
            continue

        query = input("\n🔍 Enter mod/plugin name: ").strip()
        if not query:
            continue

        results = search_modrinth(query, loader, mc_version)

        if not results:
            print("❌ No compatible results found")
            continue

        print("\nResults:")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['title']}")

        choice = input("\nSelect number (0 to cancel): ").strip()
        if not choice.isdigit():
            continue

        choice = int(choice)
        if choice == 0:
            continue

        index = choice - 1
        if index >= len(results):
            print("❌ Invalid choice")
            continue

        slug = results[index]["slug"]

        download_modrinth_plugin(
            slug,
            mc_version,
            loader,
            target_dir
        )

        # 🔁 ASK AGAIN
        again = input("\nInstall another mod/plugin? (y/n): ").strip().lower()
        if again != "y":
            print("✔ Finished installing mods/plugins")
            return




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
    server_name = input("Server name: ").strip()
    path = f"servers/{server_name}"

    if os.path.exists(path):
        print("❌ Server already exists")
        return

    # ---------------- SERVER TYPE (UPDATED) ----------------
    print("\n🎮 Select server type:")
    print("1. Paper (Recommended - Plugins, High Performance)")
    print("2. Purpur (Paper fork - Extra features & optimizations)")
    print("3. Vanilla (Pure Minecraft - No mods/plugins)")
    print("4. Fabric (Lightweight mods)")
    print("5. Forge (Popular mod loader)")

    server_types = {
        "1": "paper",
        "2": "purpur",
        "3": "vanilla",
        "4": "fabric",
        "5": "forge"
    }
    
    jar_type = server_types.get(input("> ").strip())
    
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

    # ---------------- CRACKED PLAYERS OPTION ----------------
    print("\n🔓 Allow cracked (non-premium) players?")
    print("Note: This disables online mode and Mojang authentication")
    online_mode_choice = input("Allow cracked players? (y/n): ").strip().lower()
    online_mode = "false" if online_mode_choice == "y" else "true"
    
    if online_mode == "false":
        print("✔ Cracked players will be allowed (online-mode=false)")
    else:
        print("✔ Only premium players allowed (online-mode=true)")

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
       elif jar_type == "purpur":
           download_purpur(version, path)
       elif jar_type == "vanilla":
           download_vanilla(version, path)
       elif jar_type == "fabric":
           download_fabric(version, path)
           setup_fabric_dirs(path)
           if input("Install Fabric API? (y/n): ").strip().lower() == "y":
               install_fabric_api(version, f"{path}/mods")
           if input("Install recommended Fabric mods? (y/n): ").strip().lower() == "y":
               install_recommended_fabric_mods(server_name, version)
       elif jar_type == "forge":
           download_forge(version, path)
           os.makedirs(f"{path}/mods", exist_ok=True)
           if input("Install recommended Forge mods? (y/n): ").strip().lower() == "y":
               install_recommended_forge_mods(server_name, version)

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

    data[server_name] = {
        "ram": ram,
        "jar": "fabric-server-launch.jar" if jar_type == "fabric" else "server.jar",
        "port": port,
        "type": jar_type,
        "description": description,
        "render_distance": render_distance,
        "difficulty": difficulty,
        "hardcore": hardcore,
        "version": version,
        "online_mode": online_mode
    }

    save_data(data)  # 🔥 MUST happen BEFORE plugins

    # ---------------- server.properties ----------------
    # Ask for world type (optional advanced setting)
    if input("\nConfigure world type? (y/n): ").strip().lower() == "y":
        world_type = ask_world_type()
    else:
        world_type = "default"
    
    with open(f"{path}/server.properties", "w") as f:
        f.write(f"server-port={port}\n")
        f.write(f"online-mode={online_mode}\n")
        f.write(f"render-distance={render_distance}\n")
        f.write(f"view-distance={render_distance}\n")
        f.write(f"difficulty={difficulty}\n")
        f.write(f"level-type={world_type}\n")
        if hardcore:
            f.write("hardcore=true\n")

    # ---------------- WORLD SETUP ----------------
    setup_world(server_name)

    # ---------------- PAPER EXTRAS ----------------
    if jar_type in ["paper", "purpur"]:
        if input("Install Geyser for Bedrock? (y/n): ").strip().lower() == "y":
            install_geyser(server_name)

        if input("Install recommended plugins? (y/n): ").strip().lower() == "y":
            if jar_type == "paper":
                install_recommended_plugins(server_name, version)
            elif jar_type == "purpur":
                install_recommended_purpur_plugins(server_name, version)
    # ---------------- DONE ----------------
    print(f"\n✔ {jar_type.upper()} server '{server_name}' created successfully!")
    print(f"🖥 Local join address: {get_local_ip()}:{port}")
    
    if online_mode == "false":
        print("🔓 Cracked players can join (online-mode is disabled)")

    if jar_type in ["paper", "purpur", "fabric", "forge"]:
       if input("Search & install mods/plugins now? (y/n): ").lower() == "y":
           mod_plugin_search_menu(server_name)

    notify_server_created(server_name, jar_type, version)


# ============================================================
# WORLD SETUP FUNCTIONS - Add these to your server_manager.py
# ============================================================

def setup_world(server_name):
    """
    Give user 3 options for world setup:
    1. Import existing world
    2. Set a custom seed
    3. Random seed (do nothing)
    """
    print("\n🌍 World Setup")
    print("1. Import existing world")
    print("2. Set a custom seed")
    print("3. Random seed (default)")
    
    choice = input("> ").strip()
    
    if choice == "1":
        # Import world
        import_world(server_name)
        
    elif choice == "2":
        # Set custom seed
        seed = input("Enter world seed: ").strip()
        
        if seed:
            server_path = f"servers/{server_name}"
            props_file = os.path.join(server_path, "server.properties")
            
            # Read existing properties
            if os.path.exists(props_file):
                with open(props_file, "r") as f:
                    lines = f.readlines()
                
                # Update or add seed
                with open(props_file, "w") as f:
                    seed_found = False
                    for line in lines:
                        if line.startswith("level-seed="):
                            f.write(f"level-seed={seed}\n")
                            seed_found = True
                        else:
                            f.write(line)
                    
                    # Add seed if not found
                    if not seed_found:
                        f.write(f"level-seed={seed}\n")
                
                print(f"✔ World seed set to: {seed}")
            else:
                print("⚠ server.properties not found")
        else:
            print("⚠ No seed entered, will use random seed")
    
    elif choice == "3":
        # Random seed - do nothing
        print("✔ Will generate world with random seed")
    
    else:
        print("⚠ Invalid choice, will use random seed")


def ask_world_type():
    """Ask for world type (normal, flat, large biomes, amplified)"""
    print("\n🌎 Select world type:")
    print("1. Normal (default)")
    print("2. Flat (superflat)")
    print("3. Large Biomes")
    print("4. Amplified (extreme hills)")
    
    world_types = {
        "1": "default",
        "2": "flat",
        "3": "large_biomes",
        "4": "amplified"
    }
    
    choice = input("> ").strip()
    world_type = world_types.get(choice, "default")
    
    print(f"✔ World type: {world_type}")
    return world_type



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


def list_files(folder, endswith=".jar"):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if f.endswith(endswith)]


def remove_file(folder, filename):
    path = os.path.join(folder, filename)
    if os.path.exists(path):
        os.remove(path)
        print(f"🗑 Removed {filename}")
    else:
        print("❌ File not found")

def manage_paper_plugins(server_name, mc_version):
    plugins_dir = f"servers/{server_name}/plugins"

    while True:
        print("\n--- Plugins (Paper) ---")
        print("1. Install Recommended Plugins")
        print("2. Search & Install Plugin")
        print("3. List Installed Plugins")
        print("4. Remove Plugin")
        print("5. Back")

        c = input("> ").strip()

        if c == "1":
            install_recommended_plugins(server_name, mc_version)

        elif c == "2":
            mod_plugin_search_menu(server_name)

        elif c == "3":
            plugins = list_files(plugins_dir)
            if not plugins:
                print("❌ No plugins installed")
            else:
                print("\nInstalled Plugins:")
                for p in plugins:
                    print("-", p)

        elif c == "4":
            plugins = list_files(plugins_dir)
            if not plugins:
                print("❌ No plugins to remove")
                continue
            for i, p in enumerate(plugins, 1):
                print(f"{i}. {p}")

            idx = input("Select plugin numbers (comma-separated): ").strip()
            if not idx:
                continue

            indexes = []
            for x in idx.split(","):
                x = x.strip()
                if x.isdigit():
                    i = int(x) - 1
                    if 0 <= i < len(plugins):
                        indexes.append(i)

            for i in sorted(set(indexes), reverse=True):
                remove_file(plugins_dir, plugins[i])


        elif c == "5":
            return


def manage_fabric_mods(server_name, mc_version):
    mods_dir = f"servers/{server_name}/mods"

    while True:
        print("\n--- Mods (Fabric) ---")
        print("1. Install Recommended Mods")
        print("2. Search & Install Mod")
        print("3. List Installed Mods")
        print("4. Remove Mod")
        print("5. Back")

        c = input("> ").strip()

        if c == "1":
            install_recommended_fabric_mods(server_name, mc_version)

        elif c == "2":
            mod_plugin_search_menu(server_name)

        elif c == "3":
            mods = list_files(mods_dir)
            if not mods:
                print("❌ No mods installed")
            else:
                print("\nInstalled Mods:")
                for m in mods:
                    print("-", m)

        elif c == "4":
            mods = list_files(mods_dir)
            if not mods:
                print("❌ No mods to remove")
                continue
            for i, m in enumerate(mods, 1):
                print(f"{i}. {m}")

            idx = input("Select mod numbers (comma-separated): ").strip()
            if not idx:
                continue

            indexes = []
            for x in idx.split(","):
                x = x.strip()
                if x.isdigit():
                    i = int(x) - 1
                    if 0 <= i < len(mods):
                        indexes.append(i)
            for i in sorted(set(indexes), reverse=True):
                remove_file(mods_dir, mods[i])


        elif c == "5":
            return



def edit_server():
    name = input("Enter server name to edit: ").strip()
    data = load_data()

    if name not in data:
        print("❌ Server not found")
        return

    server = data[name]
    server_path = f"servers/{name}"

    while True:
        print("\n==============================")
        print(f" Edit Server: {name}")
        print("==============================")
        print(f"Type: {server['type']}")
        print(f"Version: {server['version']}")
        print(f"Online Mode: {server.get('online_mode', 'true')}")
        print("1. Server Settings")
        print("2. Mods / Plugins")
        print("3. Server Software")
        print("4. Save & Exit")
        print("5. Change world")
        print("6. Cancel")

        choice = input("> ").strip()

        # SERVER SETTINGS
        if choice == "1":
            print("\n--- Server Settings ---")
            print("1. Change Difficulty")
            print("2. Change Render Distance")
            print("3. Toggle Hardcore")
            print("4. Toggle Online Mode (Allow/Disallow Cracked Players)")
            print("5. Back")

            s = input("> ").strip()

            if s == "1":
                server["difficulty"] = ask_difficulty()
                
            elif s == "2":
                server["render_distance"] = ask_render_distance()
                
            elif s == "3":
                server["hardcore"] = not server.get("hardcore", False)
                print(f"Hardcore: {server['hardcore']}")
                
            elif s == "4":
                current_mode = server.get("online_mode", "true")
                print(f"\nCurrent: online-mode={current_mode}")
                print("online-mode=true  → Only premium players (default)")
                print("online-mode=false → Allows cracked/non-premium players")
                
                toggle = input("\nToggle to allow cracked players? (y/n): ").strip().lower()
                
                if toggle == "y":
                    new_mode = "false" if current_mode == "true" else "true"
                    server["online_mode"] = new_mode
                    
                    # Update server.properties
                    props_path = os.path.join(server_path, "server.properties")
                    if os.path.exists(props_path):
                        with open(props_path, "r") as f:
                            lines = f.readlines()
                        
                        with open(props_path, "w") as f:
                            found = False
                            for line in lines:
                                if line.startswith("online-mode="):
                                    f.write(f"online-mode={new_mode}\n")
                                    found = True
                                else:
                                    f.write(line)
                            
                            if not found:
                                f.write(f"online-mode={new_mode}\n")
                        
                        print(f"✔ Updated: online-mode={new_mode}")
                        
                        if new_mode == "false":
                            print("🔓 Cracked players can now join")
                        else:
                            print("🔒 Only premium players can join")
                    else:
                        print("⚠ server.properties not found")

        # MODS / PLUGINS
        if server["type"] in ["paper", "purpur"]:
            manage_paper_plugins(name, server["version"])
        elif server["type"] in ["fabric", "forge"]:
            manage_fabric_mods(name, server["version"])
        else:
            print("⚠ Vanilla does not support mods/plugins")

        # SERVER SOFTWARE
        if choice == "3":
            print("\n--- Server Software ---")
            print("1. Change Minecraft Version")
            print("2. Back")
            s = input("> ").strip()
            if s == "1":
                server["version"] = input("Enter new version: ").strip()

        # SAVE
        elif choice == "4":
            save_data(data)
            print("✔ Changes saved")
            
            # Apply changes to server.properties
            props_path = os.path.join(server_path, "server.properties")
            if os.path.exists(props_path):
                try:
                    with open(props_path, "r") as f:
                        lines = f.readlines()
                    
                    with open(props_path, "w") as f:
                        settings_map = {
                            "difficulty": server.get("difficulty", "normal"),
                            "render-distance": server.get("render_distance", 10),
                            "view-distance": server.get("render_distance", 10),
                            "hardcore": "true" if server.get("hardcore", False) else "false",
                            "online-mode": server.get("online_mode", "true")
                        }
                        
                        updated_keys = set()
                        
                        for line in lines:
                            written = False
                            for key, value in settings_map.items():
                                if line.startswith(f"{key}="):
                                    f.write(f"{key}={value}\n")
                                    updated_keys.add(key)
                                    written = True
                                    break
                            
                            if not written:
                                f.write(line)
                        
                        # Add any missing settings
                        for key, value in settings_map.items():
                            if key not in updated_keys:
                                f.write(f"{key}={value}\n")
                    
                    print("✔ server.properties updated")
                except Exception as e:
                    print(f"⚠ Could not update server.properties: {e}")
            
            return

        # CANCEL
        elif choice == "6":
            print("❌ Edit cancelled")
            return

        elif choice == "5":
            import_world(name)



# -------------------- Server Management --------------------





"""
START SERVER - ALL WINDOWS AUTO-CLOSE
Everything closes automatically when server stops - clean and simple
"""

def start_server(server_name):
    data = load_data()
    if server_name not in data:
        print("❌ Server not found")
        return

    server = data[server_name]
    path = f"servers/{server_name}"
    jar = server.get("jar", "server.jar")
    ram = server["ram"]
    port = server["port"]
    server_type = server.get("type", "vanilla")

    abs_path = os.path.abspath(path)
    
    running_file = os.path.join(path, "running.txt")
    if os.path.exists(running_file):
        print("❌ Server is already running")
        return

    command_file = os.path.join(path, "command.txt")
    if os.path.exists(command_file):
        os.remove(command_file)

    print(f"\n▶ Starting server '{server_name}' on port {port} with {ram} RAM...")
    
    # ============ FORGE SERVERS ============
    if server_type == "forge":
        forge_run_bat = os.path.join(abs_path, "run.bat")
        
        if not os.path.exists(forge_run_bat):
            print(f"❌ Forge server not installed!")
            print(f"\n📍 Go to: {abs_path}")
            print(f"🔧 Run: INSTALL_FORGE.bat")
            return
        
        # Create launcher that calls Forge's run.bat
        launcher_file = os.path.join(abs_path, "start_forge.bat")
        with open(launcher_file, "w") as f:
            f.write('@echo off\n')
            f.write(f'title Minecraft Server - {server_name} (Forge)\n')
            f.write(f'cd /d "{abs_path}"\n')
            f.write('call run.bat\n')
            f.write('pause\n')
        
        try:
            process = subprocess.Popen(
                f'start "Forge Server - {server_name}" cmd /k "{launcher_file}"',
                cwd=abs_path,
                shell=True
            )
            print(f"✔ Forge server console opened")
        except Exception as e:
            print(f"❌ Failed to start: {e}")
            return
    
    # ============ OTHER SERVERS ============
    else:
        jar_path = os.path.join(abs_path, jar)
        
        if not os.path.exists(jar_path):
            print(f"❌ JAR file not found: {jar}")
            return
        
        launcher_file = os.path.join(abs_path, "run_server.bat")
        with open(launcher_file, "w") as f:
            f.write('@echo off\n')
            f.write(f'title Minecraft Server - {server_name}\n')
            f.write(f'cd /d "{abs_path}"\n')
            f.write(f'java -Xms{ram} -Xmx{ram} -jar "{jar}" nogui\n')
            f.write('pause\n')
        
        try:
            subprocess.Popen(
                f'start "Minecraft Server - {server_name}" cmd /k "{launcher_file}"',
                cwd=abs_path,
                shell=True
            )
            print(f"✔ Server console opened")
        except Exception as e:
            print(f"❌ Failed to start: {e}")
            return

    # ============ IMPROVED PROCESS DETECTION ============
    print("⏳ Waiting for server to start...")
    time.sleep(3)  # Initial wait
    
    java_pid = None
    max_attempts = 5
    
    for attempt in range(max_attempts):
        print(f"🔍 Looking for Java process (attempt {attempt + 1}/{max_attempts})...")
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
                try:
                    if not proc.info['name'] or 'java' not in proc.info['name'].lower():
                        continue
                    
                    cmdline = proc.info.get('cmdline', [])
                    if not cmdline:
                        continue
                    
                    cmdline_str = ' '.join(str(c) for c in cmdline).lower()
                    
                    # Multiple detection methods
                    is_our_server = False
                    
                    # Method 1: Check for jar name
                    if jar.lower() in cmdline_str:
                        is_our_server = True
                    
                    # Method 2: Check for server folder in working directory
                    try:
                        proc_cwd = proc.info.get('cwd', '')
                        if proc_cwd and abs_path.lower() in proc_cwd.lower():
                            is_our_server = True
                    except:
                        pass
                    
                    # Method 3: For Forge - check for libraries folder reference
                    if server_type == "forge" and "libraries" in cmdline_str:
                        try:
                            proc_cwd = proc.info.get('cwd', '')
                            if abs_path.lower() in proc_cwd.lower():
                                is_our_server = True
                        except:
                            pass
                    
                    # Method 4: Check for nogui argument (standard servers)
                    if "nogui" in cmdline_str:
                        try:
                            proc_cwd = proc.info.get('cwd', '')
                            if abs_path.lower() in proc_cwd.lower():
                                is_our_server = True
                        except:
                            pass
                    
                    if is_our_server:
                        java_pid = proc.info['pid']
                        print(f"✔ Found Java process: PID {java_pid}")
                        break
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"⚠ Search error: {e}")
        
        if java_pid:
            break
        
        if attempt < max_attempts - 1:
            print(f"⏳ Waiting 2 more seconds...")
            time.sleep(2)
    
    # Save PID or search info
    if java_pid:
        with open(running_file, "w") as f:
            f.write(str(java_pid))
        print(f"✔ Server PID saved: {java_pid}")
    else:
        # Fallback: Save search criteria
        print(f"⚠ Could not detect PID, using fallback tracking")
        with open(running_file, "w") as f:
            # Save multiple search criteria
            f.write(f"SEARCH:{server_name}:{jar}:{abs_path}")
        print(f"✔ Server tracking enabled (fallback mode)")

    print(f"\n✔ Server '{server_name}' started!")
    print(f"🖥 Join: {get_local_ip()}:{port}")
    
    if server_type == "forge":
        print(f"\n💡 Forge server may take longer to fully start")

    # ============ START HELPER PROCESSES ============
    
    # Only start helpers if we have a PID (for reliable tracking)
    if java_pid:
        # Health monitor
        # Health monitor - Direct launch (no wrapper!)
        try:
            health_monitor_path = os.path.abspath("core/health_monitor.py")
            if os.path.exists(health_monitor_path):
                subprocess.Popen(
                    f'start "Health Monitor - {server_name}" python "{health_monitor_path}" {server_name}',
                    shell=True
                    )
                print("✔ Health monitor started")
        except Exception as e:
            print(f"⚠ Could not start health monitor: {e}")

        # Watcher
        try:
            watcher_path = os.path.abspath("server_watcher.py")
            if os.path.exists(watcher_path):
                subprocess.Popen(
                    f'start "Watcher - {server_name}" python "{watcher_path}" {server_name} {java_pid}',
                    shell=True
                )
                print("✔ Watcher started")
        except Exception as e:
            print(f"⚠ Could not start watcher: {e}")
    else:
        print(f"\n⚠ Helper processes not started (PID detection failed)")
        print(f"   Server is running, but you'll need to stop it manually")

    # Notification
    try:
        from notifications import notify_server_start
        notify_server_start(server_name, port, server_type)
    except:
        pass



def stop_server(server_name):
    """Stop server with improved process detection"""
    path = f"servers/{server_name}"
    running_file = os.path.join(path, "running.txt")
    command_file = os.path.join(path, "command.txt")

    if not os.path.exists(running_file):
        print("❌ Server is not running")
        return

    try:
        with open(running_file, "r") as f:
            content = f.read().strip()
    except:
        print("❌ Could not read running file")
        return

    print(f"⛔ Stopping server '{server_name}'...")

    # Get PID
    java_pid = None
    
    if content.startswith("SEARCH:"):
        # Format: SEARCH:server_name:jar:path
        parts = content.split(":")
        search_jar = parts[2] if len(parts) > 2 else "server.jar"
        search_path = parts[3] if len(parts) > 3 else ""
        
        print(f"🔍 Searching for server process...")
        
        # Find the Java process with multiple methods
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
            try:
                if not proc.info['name'] or 'java' not in proc.info['name'].lower():
                    continue
                
                cmdline = proc.info.get('cmdline', [])
                if not cmdline:
                    continue
                
                cmdline_str = ' '.join(str(c) for c in cmdline).lower()
                
                # Multiple detection methods
                found = False
                
                # By jar name
                if search_jar.lower() in cmdline_str:
                    found = True
                
                # By working directory
                if search_path:
                    try:
                        proc_cwd = proc.info.get('cwd', '').lower()
                        if proc_cwd and search_path.lower() in proc_cwd:
                            found = True
                    except:
                        pass
                
                if found:
                    java_pid = proc.info['pid']
                    print(f"✔ Found server process: PID {java_pid}")
                    break
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not java_pid:
            print("❌ Could not find server process")
            print("💡 Try closing the server console window manually")
            cleanup_files(running_file, command_file)
            return
    else:
        # Direct PID
        java_pid = int(content)

    print(f"🎯 Stopping PID: {java_pid}")

    # Method 1: Watcher
    watcher_path = os.path.abspath("server_watcher.py")
    if os.path.exists(watcher_path):
        try:
            with open(command_file, "w") as f:
                f.write("stop")
            print("📝 Stop command sent to watcher")
            
            for i in range(10):
                if not psutil.pid_exists(java_pid):
                    print(f"✔ Server stopped")
                    cleanup_files(running_file, command_file)
                    
                    try:
                        from notifications import notify_server_stop
                        notify_server_stop(server_name)
                    except:
                        pass
                    
                    return
                time.sleep(1)
        except:
            pass

    # Method 2: Direct termination
    print(f"🔪 Terminating process...")
    
    try:
        proc = psutil.Process(java_pid)
        proc.terminate()
        
        for i in range(5):
            if not proc.is_running():
                print("✔ Server stopped")
                cleanup_files(running_file, command_file)
                
                try:
                    from notifications import notify_server_stop
                    notify_server_stop(server_name)
                except:
                    pass
                
                return
            time.sleep(1)
        
        proc.kill()
        time.sleep(2)
        
    except psutil.NoSuchProcess:
        print("✔ Process already stopped")
    except Exception as e:
        print(f"⚠ Error: {e}")
    
    # Method 3: Taskkill
    print("🔪 Using taskkill...")
    os.system(f"taskkill /F /PID {java_pid} /T >nul 2>&1")
    time.sleep(2)
    
    cleanup_files(running_file, command_file)
    print(f"✔ Server '{server_name}' stopped")
    
    try:
        from notifications import notify_server_stop
        notify_server_stop(server_name)
    except:
        pass


def cleanup_files(running_file, command_file):
    """Clean up tracking files"""
    for file in [running_file, command_file]:
        if os.path.exists(file):
            try:
                os.remove(file)
            except:
                pass


def force_stop_server(server_name):
    """
    Force stop without any grace period
    Use this when regular stop doesn't work
    """
    path = f"servers/{server_name}"
    running_file = os.path.join(path, "running.txt")
    command_file = os.path.join(path, "command.txt")
    
    if not os.path.exists(running_file):
        print("❌ Server is not running")
        return
    
    data = load_data()
    server = data.get(server_name)
    if not server:
        print("❌ Server config not found")
        return
    
    jar = server.get('jar', 'server.jar')
    server_type = server.get('type', 'vanilla')
    
    print(f"💥 Force stopping '{server_name}'...")
    
    # Kill all java processes running this server
    killed = False
    killed_count = 0
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'java' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline', [])
                cmdline_str = ' '.join(cmdline) if cmdline else ''
                
                # Check if this Java process belongs to our server
                if jar in cmdline_str or server_name in cmdline_str:
                    pid = proc.info['pid']
                    print(f"🔪 Killing PID {pid}")
                    os.system(f"taskkill /F /PID {pid} /T >nul 2>&1")
                    killed = True
                    killed_count += 1
        except:
            continue
    
    if not killed:
        print("⚠ No matching process found")
    else:
        print(f"✔ Killed {killed_count} process(es)")
    
    cleanup_files(running_file, command_file)
    print(f"✔ Force stop complete")
    
    # Send notification
    try:
        from notifications import notify_server_stop
        notify_server_stop(server_name)
    except:
        pass


def restart_server(server_name):
    """Restart a server"""
    print(f"🔄 Restarting server '{server_name}'...")
    
    stop_server(server_name)
    
    # Wait for cleanup
    print("⏳ Waiting for cleanup...")
    time.sleep(5)
    
    start_server(server_name)
    print(f"✔ Server '{server_name}' restarted")


def is_server_running(server_name):
    """Check if a server is running with improved detection"""
    path = f"servers/{server_name}"
    running_file = os.path.join(path, "running.txt")
    
    if not os.path.exists(running_file):
        return False
    
    try:
        with open(running_file, "r") as f:
            content = f.read().strip()
        
        if content.startswith("SEARCH:"):
            # Format: SEARCH:server_name:jar:path
            parts = content.split(":")
            if len(parts) < 4:
                return False
            
            search_name = parts[1]
            search_jar = parts[2]
            search_path = parts[3]
            
            # Search for the process
            for proc in psutil.process_iter(['name', 'cmdline', 'cwd']):
                try:
                    if not proc.info['name'] or 'java' not in proc.info['name'].lower():
                        continue
                    
                    cmdline = proc.info.get('cmdline', [])
                    if not cmdline:
                        continue
                    
                    cmdline_str = ' '.join(str(c) for c in cmdline).lower()
                    
                    # Check multiple criteria
                    if search_jar.lower() in cmdline_str:
                        return True
                    
                    try:
                        proc_cwd = proc.info.get('cwd', '').lower()
                        if proc_cwd and search_path.lower() in proc_cwd:
                            return True
                    except:
                        pass
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return False
        else:
            # Direct PID check
            pid = int(content)
            return psutil.pid_exists(pid)
            
    except Exception as e:
        print(f"Error checking server status: {e}")
        return False



def delete_server(name):
    path = f"servers/{name}"

    notify_server_deleted(name)

    # 1. Stop server if running
    if is_server_running(name):
        print(f"⛔ Stopping server '{name}' before deletion...")
        pid = get_server_pid(name)

        stop_server(name)

        # wait up to 15 seconds
        for _ in range(15):
            if not psutil.pid_exists(pid):
                break
            time.sleep(1)

        # force kill if still alive
        if psutil.pid_exists(pid):
            print("⚠ Server did not stop, force killing...")
            try:
                psutil.Process(pid).kill()
            except psutil.NoSuchProcess:
                pass
            time.sleep(2)

    # 2. Delete folder (the folder itself)
    if os.path.exists(path):
        force_delete_folder(path)

    # 3. Remove metadata
    data = load_data()
    if name in data:
        del data[name]
        save_data(data)

    print(f"✔ Server '{name}' deleted successfully")

def force_delete_folder(path, retries=5):
    """
    Deletes the FOLDER ITSELF (not just contents)
    Windows-safe with retries + rename fallback
    """
    for _ in range(retries):
        try:
            shutil.rmtree(path)
            return
        except PermissionError:
            time.sleep(1)

    # rename fallback (very effective on Windows)
    tmp = path + "_deleting"
    os.rename(path, tmp)
    shutil.rmtree(tmp)

def get_server_pid(server_name):
    path = f"servers/{server_name}"
    running_file = os.path.join(path, "running.txt")
    try:
        with open(running_file, "r") as f:
            return int(f.read().strip())
    except:
        return None


