# CopyTree

CopyTree is a command-line tool for creating ASCII file trees and replicating file trees using `.ct` files. It allows you to easily visualize and duplicate directory structures.

## Features

- Generate ASCII representations of directory trees
- Replicate directory structures using `.ct` files
- Export directory structures to `.ct` files
- Enable pirate-speak mode for fun logging messages
- uhh copytree = cool

## Installation

To install CopyTree, you have two options:



### Install via pip

```sh
pip install copytree-cli
```

## Usage

To use CopyTree, run the following command:

```sh
copytree [options]
```

or
```sh
ct [options]
```

### Options

- `-v, --verbose` : Enable verbose output
- `-e, --export [file]` : Export the structure to a file (default: export.ct)
- `-d, --directory [directory]` : Directory to copy
- `-b, --build [file]` : Build structure based on a `.ct` file
- `-h, --help` : Display help information

## Examples

Generate an ASCII file tree for the current directory:

```sh
copytree
```

Replicate a directory tree from a `.ct` file:

```sh
copytree -b tree.ct
```

Export the current directory structure to a `.ct` file:

```sh
copytree -e my_structure.ct
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please contact [meepstertron@gmail.com](mailto:meepstertron@gmail.com).
