---

# greplinks

`greplinks` is a lightweight command-line tool designed to extract and validate URLs from text inputs (files or standard input). It supports various protocols, IPv4/IPv6 addresses, domain names, and advanced validation features such as port checks, query string validation, and fragment handling.

---

## Table of Contents
1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Command-Line Arguments](#command-line-arguments)
5. [Examples](#examples)
6. [Contributing](#contributing)
7. [License](#license)
8. [Acknowledgments](#acknowledgments)

---

## Features

- Extracts URLs from plain text inputs.
- Supports:
  - Common protocols: `http`, `https`, `ftp`, `sftp`, `ssh`, `git`, etc.
  - IPv4 and IPv6 addresses.
  - Domain names with or without schemes.
- Validates URLs using strict rules:
  - Ensures valid ports (0–65535).
  - Checks paths, query strings, and fragments.
  - Strict IPv4 and IPv6 validation.
- Optional features:
  - Colorized output for better readability.
  - Sorting extracted URLs alphabetically.
  - Silent mode to suppress console output.
- Handles both file inputs and standard input/output.

---

## Installation

### Prerequisites
- Python 3.9+ installed on your system.

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/a-mashhoor/greplinks.git
   cd greplinks
   ```
2. Make the script executable:
   ```bash
   chmod +x greplinks.py
   ```

3. Run the tool:
   ```bash
   ./greplinks.py --help
   ```

---

## Usage

### Basic Syntax
```bash
python greplinks.py [-i INPUT_FILE] [-o OUTPUT_FILE] [--silent] [--colored] [--sort]
```

### Input/Output Options
- Use `-i` or `--input-file` to specify an input file.
- Use `-o` or `--output` to save the extracted URLs to a file.
- If no input file is provided, the tool reads from standard input (`stdin`).
- If no output file is specified, the results are printed to standard output (`stdout`).

---

## Command-Line Arguments

| Argument          | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| `-h, --help`      | Show the help message and exit.                                             |
| `-i, --input-file`| Read input from a file.                                                     |
| `-o, --output`    | Save the extracted URLs to a file.                                          |
| `-s, --silent`    | Suppress all output to the console.                                         |
| `-c, --colored`   | Colorize the output on the console.                                         |
| `-so, --sort`     | Sort the extracted URLs alphabetically.                                     |
| `-v, --version`   | Display the version of the tool and exit.                                   |

---

## Examples

### Example 1: Extract URLs from a File
Extract URLs from `input.txt` and print them to the console:
```bash
python greplinks.py -i input.txt
```

### Example 2: Save Output to a File
Extract URLs from `input.txt` and save them to `output.txt`:
```bash
python greplinks.py -i input.txt -o output.txt
```

### Example 3: Pipe Input from Standard Input
Pipe text from another command and print the extracted URLs:
```bash
cat input.txt | python greplinks.py
```

### Example 4: Enable Colorized Output
Extract URLs and display them in color:
```bash
python greplinks.py -i input.txt --colored
```

### Example 5: Sort the Output
Extract URLs and sort them alphabetically:
```bash
python greplinks.py -i input.txt --sort
```

---

## Contributing

Contributions are welcome! If you’d like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature description"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Submit a pull request.

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built using Python's `argparse`, `re`, `urllib.parse`, and `ipaddress` modules.
- Inspired by the need for a lightweight URL extraction and validation tool.
- Special thanks to the open-source community for their contributions and support.

---

## Author

- **Arshia Mashhoor**
- GitHub: [a-mashhoor](https://github.com/a-mashhoor)

---

