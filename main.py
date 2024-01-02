import os, json, requests
from colorama import Fore, init

init(autoreset=True)

class massLeave:
    clear: str = 'cls' if os.name == 'nt' else 'clear'
    groups_left: int = 0
    
    def __init__(self, settings):
        self.cookie = settings["cookie"]
        self.mass_leave = settings["mass_leave"]
        self.whitelist = set(settings.get("whitelist", []))
        self.user_id = self.get_id()
        self.csrf = self.get_csrf()
        self.groups = self.get_groups()
    
    def get_id(self):
        response = requests.get("https://users.roblox.com/v1/users/authenticated", cookies={".ROBLOSECURITY": self.cookie}).json()
        assert response.get("id"), Fore.RED + "Please provide a valid cookie in settings.json"
        return response["id"]
    
    def get_csrf(self):
        return requests.post("https://economy.roblox.com/", cookies={".ROBLOSECURITY": self.cookie}).headers['x-csrf-token']
    
    def get_groups(self):
        response = requests.get(f'https://groups.roblox.com/v2/users/{self.user_id}/groups/roles')
        assert response.status_code == 200, Fore.RED + f"Failed to fetch groups. {response.status_code}"
        return response.json().get('data', [])
    
    def leave_groups(self):
        if self.mass_leave:
            input(Fore.LIGHTRED_EX + "!!! Warning: Mass leave is enabled. This will leave all the groups you're in except the groups you've added in the whitelist! Press Enter to continue.")
            os.system(self.clear)
        print(Fore.GREEN + f"You are currently in {len(self.groups)} groups.\n")
        
        for group in self.groups:
            self.leave_group(group)
        
        print(Fore.MAGENTA + f"Left {self.groups_left} groups.")
        os.system("pause")
        
    def leave_group(self, group):
        group_name = group['group']['name']
        group_id = group['group']['id']
        group_rank = group["role"]['rank']
        if group_id not in self.whitelist:
            leave = 'y' if self.mass_leave else print(Fore.YELLOW + f"Skipping group (owned): {group_name} (ID: {group_id})") if group_rank == 255 else input(Fore.LIGHTRED_EX + f"Do you want to leave group {group_name} (ID: {group_id})? (y/n): ").strip().lower()
            if leave == 'y':
                if group_rank == 255:
                    return print(Fore.YELLOW + f"Skipping group (owned): {group_name} (ID: {group_id})")
                else:
                    total_retries = 0
                    while total_retries < 2:
                        response = requests.delete(f'https://groups.roblox.com/v1/groups/{self.user_id}/users/{group_id}', cookies={".ROBLOSECURITY": self.cookie}, headers={"x-csrf-token": self.csrf})
                        if response.status_code == 200:
                            self.groups_left += 1
                            return print(Fore.GREEN + f"Left group: {group_name} (ID: {group_id})")
                        elif response.status_code == 401:
                            self.csrf = self.get_csrf()
                        else:
                            return print(Fore.RED + f"Failed to leave group: {group_name} (ID: {group_id}) {response.status_code}")
                    return
            else:
                return
        else:
            return print(Fore.YELLOW + f"Skipping group: {group_name} (ID: {group_id})")
          
if __name__ == "__main__":
    massLeave(json.loads(open("settings.json", 'r').read())).leave_groups()
