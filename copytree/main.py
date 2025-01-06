import argparse
import os
import json
import errno
import threading
import pkg_resources


pirate = False

verbose = False
def log(message):
    if verbose:
        if isinstance(message, str) and pirate:
            message = translate_to_pirate(message)
        print(f"[INFO] {message}")

def translate_to_pirate(message):
    pirate_dict = {
        "INFO": "ARRR, ye be needin' info!",
        "Config file not found, creating one": "Arrr, the config file be missin'! We be creatin' one right now, aye!",
        "Verbose mode enabled": "Verbose mode be enabled, ye scurvy dog!",
        "Exporting to file": "Arrr, we be exportin' it to a fine file, matey!",
        "Copying directory": "Aye, copyin' that entire treasure chest o' directory!",
        "Copying current directory": "Copyin' this here current directory, ye landlubber!",
        "Root": "Yer root, the heart o' the ship!",
        "Directory": "Diirrrrectory, where all yer treasures be stashed!",
        "File": "A file, a map to yer treasure, arr!",
        "Current copy": "This be the current copy, ye savvy?",
        "Timeout reached while walking through": "Arrr, timeout reached while we be walkin' the plank, I mean, through the seas!",
        "Permission error": "Permission denied, ye scurvy pirate! Ye don't have the captain's key!",
        
    }

    for key, value in pirate_dict.items():
        message = message.replace(key, value)
    return message

def build_tree(obj, path):
    for key, value in obj.items():
        if isinstance(value, str):
            with open(os.path.join(path, key+value), 'w') as file:
                file.write("")
       
        if isinstance(value, dict):
            new_path = os.path.join(path, key)
            try:
                os.makedirs(new_path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            build_tree(value, new_path)


def load_config():
    global pirate
    config_path = os.path.expanduser("~") + "/.copytree/config.json"
    if os.path.isfile(config_path):
        with open(config_path, 'r') as file:
            config = json.load(file)
            if "pirate-speak" in config and config["pirate-speak"]:
                pirate = True
            return config
    else:
        return {"folder-prefix": "/", "sub-file-indicator": "├──", "end-cap-indicator":"└──"}

def create_default_config(config_path):
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as file:
        json.dump({"folder-prefix": "/", "sub-file-indicator": "├──", "end-cap-indicator":"└──", "indent-space-indicator": "│", "pirate-speak": False, "color": False, "folder-color": "33", "default-file-color": "32", "file-type-colors": [{"c": "45", "ext": "ct"}], "root-color": "43", "compact": False}, file, indent=4)

def get_top_most_folder_name(path):

    head, tail = os.path.split(path)

    if not tail:
        head, tail = os.path.split(head)

    return tail

def remove_dot_from_extension(extension):
    return extension[1:] if extension.startswith('.') else extension

def if_color(color, text):
    if not config["color"]:
        return text
    return f"\033[{color}m{text}\033[0m"

def print_tree(data, indent="", is_last=True, is_root=False, config=None):
    if isinstance(data, dict):
        for count, (key, value) in enumerate(data.items()):
            is_directory = isinstance(value, dict)
            
           
            if is_root:
                message = f"{indent}{if_color(config['root-color'], config['folder-prefix'] + key)}"
                if pirate:
                    message = translate_to_pirate(message)
                print(message)  
                new_indent = indent + " "
            else:
                if is_directory:
                    prefix = if_color(config['folder-color'], f"{config['folder-prefix']}{key}") 
                else:
                    file_extension = remove_dot_from_extension(os.path.splitext(key)[1])
                    file_color = next((item['c'] for item in config['file-type-colors'] if 'ext' in item and item['ext'] == file_extension), config['default-file-color'])
                    prefix = if_color(file_color, f"{key}")
                      
                
                if count == len(data) - 1:
                    message = f"{indent}{config['end-cap-indicator']} {prefix}"
                    new_indent = indent + "    "
                else:
                    message = f"{indent}{config['sub-file-indicator']} {prefix}"
                    new_indent = indent + f"{config['indent-space-indicator']}   "
                
                if pirate:
                    message = translate_to_pirate(message)
                print(message)
            
            print_tree(value, new_indent, count == len(data) - 1, is_root=False, config=config)
    elif isinstance(data, str):
        message = f"{indent}{config['end-cap-indicator']} {data}"
        if pirate:
            message = translate_to_pirate(message)
        print(message)  # Print file without "/"

def format_tree(data):
    formatted_data = {}
    for key, value in data.items():
        if isinstance(value, dict):
            formatted_data[key] = format_tree(value)
        else:
            # Add file extension directly in the tree structure
            formatted_data[f"{key}.{value}"] = None
    return formatted_data

def ensure_dict_structure(current_level, parts):
    for part in parts:
        if part not in current_level or not isinstance(current_level[part], dict):
            current_level[part] = {}
        current_level = current_level[part]
    return current_level

class TimeoutException(Exception):
    pass

def safe_os_walk(directory, timeout=10):
    def timeout_handler():
        raise TimeoutException

    timer = threading.Timer(timeout, timeout_handler)
    timer.start()

    try:
        for root, dirs, files in os.walk(directory):
            yield root, dirs, files
        timer.cancel()
    except TimeoutException:
        log(f"Timeout reached while walking through {directory}")
    except PermissionError as e:
        log(f"Permission error: {e}")
    finally:
        timer.cancel()

def main():
    global pirate
    global verbose
    global config
    
    parser = argparse.ArgumentParser(description='Copytree command-line tool')
    parser.add_argument('command', nargs='?', choices=['copytree', 'ct'], default='copytree', help='The command to run')

    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-e', '--export', nargs='?', const='export.ct', help='Export the structure to a file (default: export.ct)')
    parser.add_argument('-d', '--directory', help='directory to copy')
    parser.add_argument('-b', '--build', help='Build structure based on CT file')
    
    # parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit')

    args = parser.parse_args()
    config_path = os.path.expanduser("~") + "/.copytree/config.json"
    if not os.path.isfile(config_path):
        log("Config file not found, creating one")
        create_default_config(config_path)
    config = load_config()

    if args.command in ['copytree', 'ct']:
        if os.path.isfile(os.path.expanduser("~") + "/.copytree/config.json"):
            log("config given exists moving on")
        else:
            log("config file not found creating one")
            os.system("mkdir -p ~/.copytree")
            os.system("cp ./config.json ~/.copytree")
            log("config file created, setting default values")
            with open(os.path.expanduser("~") + "/.copytree/config.json", 'w') as file:
                json.dump({"folder-prefix": "/", "sub-file-indicator": "├──", "end-cap-indicator":"└──",}, file, indent=4)
                

            
            
        if args.build:
            log(f"Building structure based on CT file: {args.build}")
            with open(args.build, 'r') as file:
                data = json.load(file)
                formatted_data = format_tree(data)
                print_tree(formatted_data, is_root=True, config=config)
                print("Building structure based on CT file")
                contin = input("Do you want to continue? (y/n): ")
                if contin == "y":
                    print("Continuing")
                    build_tree(data, os.getcwd())
                    
                else:
                    print("Exiting")
                    exit()
                    
                    
                    
        if args.verbose:
            print("Verbose mode enabled")
            verbose = True
            
            
            
            
        if args.export:
            log(f"Exporting to file: {args.export}")
            
            if args.directory:
                log(f"Exporting directory: {args.directory}")
                directory = args.directory
            else:
                log("Exporting current directory")
                directory = os.getcwd()
            currentcopy = {}
            rootfolder = get_top_most_folder_name(directory)

            currentcopy[rootfolder] = {}

            for root, dirs, files in safe_os_walk(directory):
                log(f"Root: {root}")
                relative_root = os.path.relpath(root, directory)
                if relative_root == ".":
                    current_level = currentcopy[rootfolder]
                else:
                    parts = relative_root.split(os.sep)
                    current_level = ensure_dict_structure(currentcopy[rootfolder], parts)

                for dir_name in dirs:
                    log(f"Directory: {os.path.join(root, dir_name)}")
                    current_level[dir_name] = {}
                for file_name in files:
                    file_nametag, file_extension = os.path.splitext(file_name)
                    current_level[file_nametag] = remove_dot_from_extension(file_extension)
                    log(f"File: {os.path.join(root, file_name)}")
                
            with open(args.export, 'w') as file:
                json.dump(currentcopy, file, indent=4)
            log("Exported to file")
            
            
            
      
            
                
                
        else:
            
            if not config["compact"]:
                print("                     _______            ")
                print("                    |__   __|           ")
                print("   ___ ___  _ __  _   _| |_ __ ___  ___ ")
                print("  / __/ _ \| '_ \| | | | | '__/ _ \/ _ \\")
                print(" | (_| (_) | |_) | |_| | | | |  __/  __/")
                print("  \___\___/| .__/ \__, |_|_|  \___|\___|")
                print("          | |     __/ |                 ")
                print(f'          |_|    |___/  {pkg_resources.get_distribution("copytree-cli").version}')
            else:
                print(if_color("1;32;40", "Copytree CLI") + " - " +if_color("1;33;40", pkg_resources.get_distribution("copytree-cli").version ))
            if args.directory:
                log(f"Exporting directory: {args.directory}")
                directory = args.directory
            else:
                log("Exporting current directory")
                directory = os.getcwd()
            currentcopy = {}
            rootfolder = get_top_most_folder_name(directory)

            currentcopy[rootfolder] = {}

            for root, dirs, files in safe_os_walk(directory):
                log(f"Root: {root}")
                relative_root = os.path.relpath(root, directory)
                if relative_root == ".":
                    current_level = currentcopy[rootfolder]
                else:
                    parts = relative_root.split(os.sep)
                    current_level = ensure_dict_structure(currentcopy[rootfolder], parts)

                for dir_name in dirs:
                    log(f"Directory: {os.path.join(root, dir_name)}")
                    current_level[dir_name] = {}
                for file_name in files:
                    file_nametag, file_extension = os.path.splitext(file_name)
                    current_level[file_nametag] = remove_dot_from_extension(file_extension)
                    log(f"File: {os.path.join(root, file_name)}")

            log("Current copy:")
            log(currentcopy)

            log(json.dumps(currentcopy, indent=4))

            formatted_data = format_tree(currentcopy)
            print_tree(formatted_data, is_root=True, config=config)

if __name__ == "__main__":
    main()