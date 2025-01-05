import argparse
import os
import json

verbose = False
def log(message):
    if verbose:
        print(f"[INFO] {message}")

def load_config():
    config_path = os.path.expanduser("~") + "/.copytree/config.json"
    if os.path.isfile(config_path):
        with open(config_path, 'r') as file:
            return json.load(file)
    else:
        return {"folder-prefix": "/", "sub-file-indicator": "├──", "end-cap-indicator":"└──"}

def create_default_config(config_path):
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as file:
        json.dump({"folder-prefix": "/", "sub-file-indicator": "├──", "end-cap-indicator":"└──"}, file, indent=4)

def get_top_most_folder_name(path):

    head, tail = os.path.split(path)

    if not tail:
        head, tail = os.path.split(head)

    return tail

def remove_dot_from_extension(extension):
    return extension[1:] if extension.startswith('.') else extension

def print_tree(data, indent="", is_last=True, is_root=False):
    if isinstance(data, dict):
        for count, (key, value) in enumerate(data.items()):
            is_directory = isinstance(value, dict)
            
            # Special case for the root directory
            if is_root:
                print(f"{indent}/{key}")  # Root directory without '└──'
                new_indent = indent + " "
            else:
                if is_directory:
                    prefix = f"/{key}"  # Add "/" for directories
                else:
                    prefix = key  # No "/" for files
                
                if count == len(data) - 1:
                    print(f"{indent}└── {prefix}")
                    new_indent = indent + "    "
                else:
                    print(f"{indent}├── {prefix}")
                    new_indent = indent + "│   "
            
            print_tree(value, new_indent, count == len(data) - 1, is_root=False)
    elif isinstance(data, str):
        print(f"{indent}└── {data}")  # Print file without "/"

def format_tree(data):
    formatted_data = {}
    for key, value in data.items():
        if isinstance(value, dict):
            formatted_data[key] = format_tree(value)
        else:
            # Add file extension directly in the tree structure
            formatted_data[f"{key}.{value}"] = None
    return formatted_data

def main():
    global verbose  
    global result
    parser = argparse.ArgumentParser(description='Copytree command-line tool')
    parser.add_argument('command', nargs='?', choices=['copytree', 'ct'], default='copytree', help='The command to run')

    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-e', '--export', nargs='?', const='export.ct', help='Export the structure to a file (default: export.ct)')
    parser.add_argument('-d', '--directory', help='directory to copy')

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

        if args.verbose:
            print("Verbose mode enabled")
            verbose = True
        if args.export:
            log(f"Exporting to file: {args.export}")
        else:
            if args.directory:
                log(f"Copying directory: {args.directory}")
                directory = args.directory
            else:
                log("Copying current directory")
                directory = os.getcwd()
                currentcopy = {}
                rootfolder = get_top_most_folder_name(directory)

                currentcopy[rootfolder] = {}

                for root, dirs, files in os.walk(directory):
                    log(f"Root: {root}")
                    relative_root = os.path.relpath(root, directory)
                    if relative_root == ".":
                        current_level = currentcopy[rootfolder]
                    else:
                        parts = relative_root.split(os.sep)
                        current_level = currentcopy[rootfolder]
                        for part in parts:
                            if part not in current_level:
                                current_level[part] = {}
                            current_level = current_level[part]

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
                print_tree(formatted_data, is_root=True)

if __name__ == "__main__":
    main()