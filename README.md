# Linkedin API Automation

This Python project provides an automated way to interact with LinkedIn using the Playwright library. It is designed to perform various tasks on LinkedIn, such as taking screenshots and processing data from Excel files.

## Features

- **Automated Login**: Logs into LinkedIn using credentials stored in an environment file.
- **Screenshot Management**: Automatically saves and manages screenshots in a dedicated folder.
- **Excel Data Processing**: Reads and processes data from an Excel file, making it ready for further operations.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.6 or higher
- Playwright library for Python
- Pandas library for data manipulation
- dotenv library for environment variable management

## Installation

To install the necessary libraries, run the following command:

```bash
pip install playwright pandas python-dotenv
```

After installation, navigate to the project directory and run the Playwright install command:

```bash
playwright install
```

## Configuration

1. Create a `.env` file in the `CREDENTIALS` directory.
2. Add your LinkedIn credentials as follows:

```env
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

3. Ensure you have an Excel file named `data.xlsx` in the `DEPENDENCY` directory for data processing.

## Usage

To use this project, run the `linkedin_api.py` script with Python. Ensure you are in the project's root directory:

```bash
python linkedin_api.py
```

## Contributing

Contributions to this project are welcome. Please fork the repository and create a pull request with your features or fixes.

## License

This project is open-source and available under the [MIT License](LICENSE).
```
