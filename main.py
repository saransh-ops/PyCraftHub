from core.server_manager import (
    create_server, edit_server, start_server,
    stop_server, restart_server, delete_server,
    list_servers, load_data, list_installed_mods
)

# ---- Splash function ----
def splash():
    print(r"""
                                                                
                                                                
$$$$$$$\             $$$$$$\                      $$$$$$\    $$\     $$\   $$\           $$\       
$$  __$$\           $$  __$$\                    $$  __$$\   $$ |    $$ |  $$ |          $$ |      
$$ |  $$ |$$\   $$\ $$ /  \__| $$$$$$\  $$$$$$\  $$ /  \__|$$$$$$\   $$ |  $$ |$$\   $$\ $$$$$$$\  
$$$$$$$  |$$ |  $$ |$$ |      $$  __$$\ \____$$\ $$$$\     \_$$  _|  $$$$$$$$ |$$ |  $$ |$$  __$$\ 
$$  ____/ $$ |  $$ |$$ |      $$ |  \__|$$$$$$$ |$$  _|      $$ |    $$  __$$ |$$ |  $$ |$$ |  $$ |
$$ |      $$ |  $$ |$$ |  $$\ $$ |     $$  __$$ |$$ |        $$ |$$\ $$ |  $$ |$$ |  $$ |$$ |  $$ |
$$ |      \$$$$$$$ |\$$$$$$  |$$ |     \$$$$$$$ |$$ |        \$$$$  |$$ |  $$ |\$$$$$$  |$$$$$$$  |
\__|       \____$$ | \______/ \__|      \_______|\__|         \____/ \__|  \__| \______/ \_______/ 
          $$\   $$ |                                                                               
          \$$$$$$  |                                                                               
           \______/                                                                                
 
                                                                

                    PyCraftHub
    Python Minecraft Server Management CLI
             Version 1.0 | by Saransh
             Made solely using Python
    """)

# ---- Call splash at start ----
splash()



def main_menu():
    while True:
        print("\n=== PyCraftHub Hosting Panel ===")
        print("1. Create Server")
        print("2. Edit Server")
        print("3. Start Server")
        print("4. Stop Server")
        print("5. Restart Server")
        print("6. Delete Server")
        print("7. List Servers")
        print("8. List mods in a server")
        print("9. Exit")
        

        choice = input("> ").strip()

        if choice == "1": create_server()
        elif choice == "2": edit_server()
        elif choice in ["3","4","5","6"]:
            data = load_data()
            if not data:
                print("❌ No servers available")
                continue
            print("\nAvailable servers:")
            server_list = list(data.keys())
            for i, name in enumerate(server_list, 1):
                print(f"{i}. {name}")
            sel = input("Select server: ").strip()
            if not sel.isdigit() or int(sel)<1 or int(sel)>len(server_list):
                print("❌ Invalid selection")
                continue
            server_name = server_list[int(sel)-1]

            if choice=="3": start_server(server_name)
            elif choice=="4": stop_server(server_name)
            elif choice=="5": restart_server(server_name)
            elif choice=="6": delete_server(server_name)

        elif choice=="7": list_servers()
        elif choice=="9":
            print("Exiting...")
            break
        elif choice == "8":
            server = input("Server name: ").strip()
            list_installed_mods(server)

        else:
            print("❌ Invalid option")

if __name__=="__main__":
    main_menu()
