import os
import subprocess

# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'

def run_command(command):
    try:
        print(f"{CYAN}Running command: {command}{RESET}")
        result = subprocess.check_output(command, shell=True, text=True).strip()
        print(f"{GREEN}Command output:\n{result}{RESET}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"{RED}Command failed with error: {e}{RESET}")
        print(f"{RED}Error output:\n{e.output}{RESET}")
        return None

def remove_fstab_entry():
    print(f"{CYAN}Removing fstab entry for 'steamgames'...{RESET}")
    current_fstab = run_command('cat /etc/fstab')
    new_fstab = '\n'.join(line for line in current_fstab.split('\n') if 'steamgames' not in line)
    run_command(f'echo "{new_fstab}" | sudo tee /etc/fstab')

def disable_remove_systemd_service():
    service_file = "/etc/systemd/system/set-steamgames-permissions.service"
    print(f"{CYAN}Disabling and removing systemd service at {service_file}...{RESET}")
    run_command('sudo systemctl disable set-steamgames-permissions.service')
    run_command(f'sudo rm {service_file}')

def remove_permission_script():
    permission_script = "/etc/systemd/system/set_steamgames_permissions.sh"
    print(f"{CYAN}Removing permission script at {permission_script}...{RESET}")
    run_command(f'sudo rm {permission_script}')

def main():
    remove_fstab_entry()
    disable_remove_systemd_service()
    remove_permission_script()

    print(f"{GREEN}Cleanup complete.{RESET}")

if __name__ == "__main__":
    main()

