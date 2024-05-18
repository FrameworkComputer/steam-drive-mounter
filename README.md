# steam-drive-mounter

## Label, auto-mount your dedicated Steam library drive/partition.

### Features:
- Detects all drives and partitions available.
- Provides a CLI prompt to select your desired games partition to be used.
- Labels said partition as steamgames (only if selected and only if not already labeled as such).
- Handles permissions and ownership automatically, plus provides the auto-mount entry in fstab.
- Creates a systemd service that checks the ownership/permissions at each boot - extreme, but it's a failsafe.
  - chown matt:matt /media/$USER/steamgames
  - chmod 700 /media/$USER/steamgames
- Seperate python script to remove the systemd service and related permission file.


### Requirements:
- Python3
- Tested on Bluefin, but should work on Fedora Workstation and Ubuntu just fine.
- Drive or partition that is formatted as ext4, ready to be used for Steam games.

  ![Step-1](https://raw.githubusercontent.com/FrameworkComputer/steam-drive-mounter/main/1.png)

  ![Step-2](https://raw.githubusercontent.com/FrameworkComputer/steam-drive-mounter/main/2.png)

  ![Step-3](https://raw.githubusercontent.com/FrameworkComputer/steam-drive-mounter/main/3.png)

### To install:
~~~
wget https://raw.githubusercontent.com/FrameworkComputer/steam-drive-mounter/main/steaminator.py && chmod+x steaminator.py
~~~

### To run it:

~~~
python3 steaminator.py 
~~~

### To remove the install:

~~~
wget https://raw.githubusercontent.com/FrameworkComputer/steam-drive-mounter/main/mount-removal.py && chmod+x mount-removal.py
~~~
