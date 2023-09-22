import os
try:
    import json
    import requests
    from colorama import Fore, init
except:
    os.system("pip install colorama")
    os.system("pip install requests")

init(autoreset=True)

def main(settings):
    os.system('cls' if os.name == 'nt' else 'clear')
    cookie = settings["cookie"]
    mass_leave = settings["mass_leave"]
    whitelist = set(settings.get("whitelist", []))
    try:
        id = requests.get("https://users.roblox.com/v1/users/authenticated", cookies={".ROBLOSECURITY": cookie}).json()["id"]
    except Exception as e:
        print(Fore.RED + "Please provide a valid cookie in settings.json")
        os.system("pause")
        return

    response = requests.get(f'https://groups.roblox.com/v2/users/{id}/groups/roles')
    if response.status_code != 200:
        print(Fore.RED + f"Failed to fetch groups. {response.status_code}")
        os.system("pause")
        return

    groups = response.json().get('data', [])
    print(Fore.GREEN + f"You are currently in {len(groups)} groups.\n")

    if mass_leave:
        input(Fore.LIGHTRED_EX + "!!! Warning: Mass leave is enabled. This will leave all the groups you're in except the groups you've added in the whitelist! Press Enter to continue.")
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.GREEN + f"You are currently in {len(groups)} groups.\n")

    groups_left = 0
    for group in groups:
        group_name = group['group']['name']
        group_id = group['group']['id']
        group_rank = group["role"]['rank']

        if group_id not in whitelist:
            if group_rank == 255:
                print(Fore.YELLOW + f"Skipping group (owned): {group_name} (ID: {group_id})")
            else:
                leave = 'y' if mass_leave else input(Fore.LIGHTRED_EX + f"Do you want to leave group {group_name} (ID: {group_id})? (y/n): ").strip().lower()

                if leave == 'y':
                    response = requests.post('https://accountsettings.roblox.com/v1/email', cookies={".ROBLOSECURITY": cookie})
                    csrf = response.headers['x-csrf-token']
                
                    response = requests.delete(f'https://groups.roblox.com/v1/groups/{group_id}/users/{id}', cookies={".ROBLOSECURITY": cookie}, headers={"x-csrf-token": csrf})
                    if response.status_code == 200:
                        print(Fore.GREEN + f"Left group: {group_name} (ID: {group_id})")
                        groups_left += 1
                    else:
                        print(Fore.RED + f"Failed to leave group: {group_name} (ID: {group_id}) {response.status_code}")
        else:
            print(Fore.YELLOW + f"Skipping group: {group_name} (ID: {group_id})")

    print(Fore.MAGENTA + f"Left {groups_left} groups.")
    os.system("pause")

if __name__ == "__main__":
    with open("settings.json", 'r') as file:
        settings = json.load(file)
    main(settings)
