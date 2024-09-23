# Cron Expression Parser

This project provides a command-line application to parse cron expressions and expand each field to show the times at which it will run. The application can handle various cron expression formats and validate them accordingly.

## Project Structure

- `cron/`
  - `__init__.py`: Initialization file for the `cron` package.
  - `constants.py`: Contains the constants for cron field ranges and supported special characters.
  - `parser.py`: Contains the `Parser` class responsible for parsing and validating cron expressions.
- `tests/`
  - `__init__.py`: Initialization file for the `tests` package.
  - `test_parser.py`: Contains test cases for the `Parser` class.
- `main.py`: The main entry point for the application.
- `README.md`: This README file.

## Installation

1. **Install Python 3.10 - Make sure given python is installed**:


2. **Create and activate a virtual environment** (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies** (if any). This project does not have additional dependencies beyond Python's standard library.

## Usage

To run the cron parser, execute the `main.py` script first, the script would then ask for  "Enter cron expression: ", Then enter your cron expression without the quotes.

Example:

```bash
python main.py 
Enter cron expression: */15 0 1,15 * 1-5 /usr/bin/find
```

## Tests
To run the tests, use Python's built-in unittest framework.
```bash
python -m unittest discover -s tests
```


5-2 -> 5 6 7 1 2

* * * * * 2023,2024 /usr/bin/find