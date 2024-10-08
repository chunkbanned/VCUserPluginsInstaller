import os
import sys
import subprocess
import shutil
import platform
import psutil
import ctypes
import stat
from consolemenu import ConsoleMenu
from consolemenu.items import FunctionItem

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
# Verify Git, Node.jS and pnpm are installed
def is_git_installed():
    try:
        result = subprocess.run(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            git_version = result.stdout.decode('utf-8').strip()
            return True, git_version
        else:
            return False, ""
    except FileNotFoundError:
        return False, ""

def is_node_installed():
    try:
        result = subprocess.run(['node', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode == 0:
            node_version = result.stdout.decode('utf-8').strip()
            return True, node_version
        else:
            return False, ""
    except FileNotFoundError:
        return False, ""


def is_pnpm_installed():
    try:
        # Use 'which' command for Unix-based systems and 'where' for Windows
        if platform.system() == "Windows":
            pnpm_path = shutil.which('pnpm')
        else:
            result = subprocess.run(['which', 'pnpm'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            pnpm_path = result.stdout.decode().strip()
        if pnpm_path:
            return pnpm_path
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
git_installed, git_version = is_git_installed();
node_installed, node_version = is_node_installed();
pnpm_installed = is_pnpm_installed();

cwd = os.getcwd()
vencord_dir = os.path.exists(cwd + "\\Vencord")

if is_admin() is False:
    print("Please run this script with administrator permissions")
    print("If you think this is sketchy, please have a look at the source code yourself!")
    sys.exit(0)

if not git_installed or not node_installed or not pnpm_installed:
    print("One of the main dependencies is not installed!")
    if not git_installed:
        print("Git must be installed for this program to run https://git-scm.com/downloads")
    elif not node_installed:
        print("Node must be installed for this program to run https://nodejs.org/en/download/package-manager")
    elif not pnpm_installed:
        print("pnpm must be installed for this program to run https://pnpm.io/installation")
    sys.exit(0)

def remove_directory(dir_path):
    # Check if the directory exists
    if os.path.exists(dir_path):
        try:
            # Change the permission of the directory and its contents to allow deletion
            for root, dirs, files in os.walk(dir_path):
                for dir in dirs:
                    os.chmod(os.path.join(root, dir), stat.S_IRWXU)
                for file in files:
                    os.chmod(os.path.join(root, file), stat.S_IRWXU)

            # Remove the directory and its contents
            shutil.rmtree(dir_path)
            print(f"Directory '{dir_path}' has been removed.")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Directory '{dir_path}' does not exist.")

def install():
    print("Please enter the Git URL or press enter to install from list")
    url = input(">> ")
    os.chdir(cwd + "\\Vencord\\src\\userplugins")
    if url == '':
        print("Installing from list...")
        if not os.path.exists(cwd + "\\list.txt"):
            print("<ERROR> 'list.txt' does not exist! Program exiting.")
            sys.exit(0)
        with open(cwd + "\\list.txt", 'r') as file:
            for line in file:
                line = line.strip()
                if not line.startswith(';') and line:
                    print(f"Cloning repository: {line}")
                    os.system("git clone " + line)
    else:
        os.system("git clone " + url)
    os.chdir(cwd + "\\Vencord")
    os.system("pnpm build")
    for process in psutil.process_iter(attrs=['pid', 'name']):
        try:
            if 'discord' in process.info['name'].lower():
                process.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    print("Finished! Please restart your Discord to apply changes.")
    input("Or press Enter to go back to the menu")

def list_installed():
    dir_names = []
    iterator = 0
    try:
        with os.scandir(cwd + "\\Vencord\\src\\userplugins") as entries:
            dir_names = [entry.name for entry in entries if entry.is_dir()]
            for name in dir_names:
                iterator = iterator + 1
                print(str(iterator) + " >> " + name)
            input("\nPress Enter to go back to the menu")
    except PermissionError:
        print("Error! Permission Error, cannot get all dirs")
        sys.exit(0)

def update():
    dir_names = []
    try:
        with os.scandir(cwd + "\\Vencord\\src\\userplugins") as entries:
            dir_names = [entry.name for entry in entries if entry.is_dir()]
    except PermissionError:
        print("Error! Permission Error, cannot get all dirs")
        sys.exit(0)

    iterator = 1
    if dir_names == []:
        print("None to update")
        input(" ")
        menu()
    print("Update")
    print("1 >> All")
    for name in dir_names:
        iterator = iterator + 1
        print(str(iterator) + " >> " + name)
    to_update = int(input(">> "))
    update_all = False
    if to_update == 1:
        update_all = True
    else:
        to_update = to_update - 2

    iterator = 0
    if update_all:
        for name in dir_names:
            os.chdir(cwd + "\\Vencord\\src\\userplugins\\" + name)
            os.system("git pull")
        os.chdir(cwd + "\\Vencord")
        os.system("pnpm build")
        for process in psutil.process_iter(attrs=['pid', 'name']):
            try:
                if 'discord' in process.info['name'].lower():
                    process.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        print("Updated all plugins successfully!")
        input("Press Enter to go back to the menu")
    else:
        for name in dir_names:
            if iterator == to_update:
                os.chdir(cwd + "\\Vencord\\src\\userplugins\\" + name)
                os.system("git pull")
                os.chdir(cwd + "\\Vencord")
                os.system("pnpm build")
                for process in psutil.process_iter(attrs=['pid', 'name']):
                    try:
                        if 'discord' in process.info['name'].lower():
                            process.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                print("Updated " + name + " successfully!")
                input("Press Enter to go back to the menu")

def uninstall():
    dir_names = []
    try:
        with os.scandir(cwd + "\\Vencord\\src\\userplugins") as entries:
            dir_names = [entry.name for entry in entries if entry.is_dir()]
    except PermissionError:
        print("Error! Permission Error, cannot get all dirs")
        sys.exit(0)

    iterator = 1
    if dir_names == []:
        print("None to uninstall")
        input(" ")
        menu()
    print("Uninstall")
    print("1 >> All")
    for name in dir_names:
        iterator = iterator + 1
        print(str(iterator) + " >> " + name)
    to_uninstall = int(input(">> "))
    if to_uninstall == 1:
        to_uninstall = to_uninstall - 1
        remove_all = True
    else:
        to_uninstall = to_uninstall - 2

    iterator = 0
    if remove_all:
        for name in dir_names:
            remove_directory(cwd + "\\Vencord\\src\\userplugins\\" + name)
        os.chdir(cwd + "\\Vencord")
        os.system("pnpm build")
        for process in psutil.process_iter(attrs=['pid', 'name']):
            try:
                if 'discord' in process.info['name'].lower():
                    process.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        print("Uninstalled all plugins successfully!")
        sys.exit(0)
    else:
        for name in dir_names:
            if iterator == to_uninstall:
                remove_directory(cwd + "\\Vencord\\src\\userplugins\\" + name)
                os.chdir(cwd + "\\Vencord")
                os.system("pnpm build")
                for process in psutil.process_iter(attrs=['pid', 'name']):
                    try:
                        if 'discord' in process.info['name'].lower():
                            process.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                print("Uninstalled " + name + " successfully!")
                sys.exit(0)

def vencordinstaller():
    os.chdir(cwd + "\\Vencord")
    os.system("pnpm inject")

def menu():
    menu = ConsoleMenu("Vencord User Plugins Installer", "Created by chunkbanned\nContributors: Plunder283")
    install_plugin = FunctionItem("Install a Plugin", install)
    list_plugin = FunctionItem("List Installed plugins", list_installed)
    uninstall_plugin = FunctionItem("Uninstall a Plugin", uninstall)
    update_plugin = FunctionItem("Update a Plugin", update)
    vencord_installer = FunctionItem("Open VencordInstaller (to uninstall, repair etc)", vencordinstaller)
    menu.append_item(install_plugin)
    menu.append_item(list_plugin)
    menu.append_item(update_plugin)
    menu.append_item(uninstall_plugin)
    menu.append_item(vencord_installer)
    menu.show()
    sys.exit(0)

if vencord_dir is True:
    menu()

print("All dependencies are installed; Git Version " + git_version + ", Node Version " + node_version)

print("Cloning Vencord Repository...")
os.system("git clone https://github.com/Vendicated/Vencord")
os.chdir(cwd + "\\Vencord")
temp_cwd = cwd.replace("\\", "/")
os.system("git config --global --add safe.directory " + temp_cwd + "/Vencord")

print("Running 'pnpm install --frozen-lockfile'")
os.system("pnpm install --frozen-lockfile")

print("Building... (this may take a while depending on your computer specifications)")
os.system("pnpm build")
os.system("cls") if os.name == "nt" else os.system("clear")
print("Running 'pnpm inject'")
print("⚠️ This will open an installer which you should choose the Install Vencord option")
os.system("pnpm inject")

print("Creating userplugins Folder")
os.chdir(cwd + "\\Vencord\\src")
os.system("mkdir userplugins")
os.chdir(cwd)
os.system("plugins")
menu()
