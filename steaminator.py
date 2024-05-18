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

def get_partition_info():
    return run_command('lsblk -ln -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT').splitlines()

def label_partition():
    partitions = get_partition_info()
    print(f"{YELLOW}Available partitions:{RESET}")
    for i, partition in enumerate(partitions):
        print(f"{BLUE}{i}: {partition}{RESET}")
    
    try:
        partition_num = int(input(f"{MAGENTA}Enter the number corresponding to the partition you wish to label as 'steamgames': {RESET}"))
        if 0 <= partition_num < len(partitions):
            partition = partitions[partition_num].split()[0]
            partition = f"/dev/{partition}"
            print(f"{MAGENTA}Selected partition: {partition}{RESET}")
            fstype = run_command(f'blkid -o value -s TYPE {partition}')
            
            if fstype in {"ext4", "ext3", "ext2", "btrfs"}:
                if fstype.startswith('ext'):
                    run_command(f'sudo e2label {partition} steamgames')
                elif fstype == 'btrfs':
                    run_command(f'sudo btrfs filesystem label {partition} steamgames')
                print(f"{GREEN}Label 'steamgames' applied to {partition}.{RESET}")
            else:
                print(f"{RED}Error: {partition} is not formatted with ext2/ext3/ext4 or btrfs filesystem.{RESET}")
                exit(1)
        else:
            print(f"{RED}Invalid selection.{RESET}")
            exit(1)
    except ValueError:
        print(f"{RED}Invalid input.{RESET}")
        exit(1)

def create_permission_script(mount_point):
    permission_script = "/etc/systemd/system/set_steamgames_permissions.sh"
    print(f"{CYAN}Creating permission script at {permission_script}...{RESET}")
    script_content = f"""#!/bin/bash
chown $USER:$USER {mount_point}
chmod 700 {mount_point}
"""
    sudo_write_file(permission_script, script_content)
    run_command(f'sudo chmod +x {permission_script}')

def sudo_write_file(path, content):
    run_command(f'echo "{content}" | sudo tee {path}')

def create_systemd_service():
    service_file = "/etc/systemd/system/set-steamgames-permissions.service"
    print(f"{CYAN}Creating systemd service at {service_file}...{RESET}")
    service_content = """[Unit]
Description=Set permissions for steamgames mount
After=local-fs.target

[Service]
Type=oneshot
ExecStart=/etc/systemd/system/set_steamgames_permissions.sh
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
"""
    sudo_write_file(service_file, service_content)
    run_command('sudo systemctl enable set-steamgames-permissions.service')

def main():
    print(f"{CYAN}Searching for volume labeled 'steamgames'...{RESET}")
    blkid_output = run_command("sudo blkid")
    if blkid_output:
        device = run_command("sudo blkid | grep -i 'LABEL=\"steamgames\"' | awk -F: '{print $1}'")
        if device:
            print(f"{GREEN}Detected device: {device}{RESET}")
        else:
            print(f"{YELLOW}No volume labeled 'steamgames' found.{RESET}")
            label_partition()
            blkid_output = run_command("sudo blkid")
            device = run_command("sudo blkid | grep -i 'LABEL=\"steamgames\"' | awk -F: '{print $1}'")
            if device:
                print(f"{GREEN}Detected device after labeling: {device}{RESET}")
            else:
                print(f"{RED}Error: No volume labeled 'steamgames' found after attempting to label a partition.{RESET}")
                exit(1)
    else:
        print(f"{RED}Error running blkid command.{RESET}")
        exit(1)

    if not device:
        print(f"{RED}Error: No volume labeled 'steamgames' found.{RESET}")
        exit(1)

    mount_point = f"/media/{os.getlogin()}/steamgames"
    print(f"{CYAN}Creating mount point at {mount_point}...{RESET}")
    run_command(f'sudo mkdir -p {mount_point}')
    run_command(f'sudo chown $USER:$USER {mount_point}')
    run_command(f'sudo chmod 700 {mount_point}')

    uuid = run_command(f'sudo blkid {device} | grep -o \'UUID="[^"]*\' | head -n 1 | cut -d\'"\' -f2')
    if uuid:
        print(f"{GREEN}Detected UUID: {uuid}{RESET}")
    else:
        print(f"{RED}Error: UUID for '{device}' not found. Please check that the device is properly labeled and exists.{RESET}")
        exit(1)

    fstype = run_command(f'sudo blkid -o value -s TYPE {device}')
    if fstype:
        print(f"{GREEN}Detected filesystem type for {device}: {fstype}{RESET}")
    else:
        print(f"{RED}Error: Filesystem type for '{device}' not found.{RESET}")
        exit(1)

    fstab_entry = f"UUID={uuid} {mount_point} {fstype} defaults 0 2"
    current_fstab = run_command('cat /etc/fstab')
    if fstab_entry not in current_fstab:
        print(f"{CYAN}Adding entry to /etc/fstab...{RESET}")
        run_command(f'echo "{fstab_entry}" | sudo tee -a /etc/fstab')
    else:
        print(f"{YELLOW}UUID already exists in /etc/fstab.{RESET}")

    create_permission_script(mount_point)
    create_systemd_service()

    print(f"{CYAN}Testing fstab entry...{RESET}")
    run_command('sudo mount -a')

    if os.path.ismount(mount_point):
        print(f"{GREEN}Volume mounted successfully at {mount_point}{RESET}")
    else:
        print(f"{RED}Error: Failed to mount the volume.{RESET}")
        exit(1)

    print(f"{GREEN}Setup complete. Please reboot your system to ensure all settings take effect.{RESET}")

if __name__ == "__main__":
    main()

