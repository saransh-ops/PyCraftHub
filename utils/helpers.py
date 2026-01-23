import os
import psutil

def get_system_ram():
    total = psutil.virtual_memory().total // (1024 ** 2)
    available = psutil.virtual_memory().available // (1024 ** 2)
    return total, available


def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    input("\nPress Enter to continue...")
