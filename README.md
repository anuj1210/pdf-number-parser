# PDF Statement Generator

This Python script generates PDF statements similar to an Airtel itemized statement, with the ability to include contact names for phone numbers.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
Simply run the script to generate a sample statement:
```bash
python generate_statement.py
```

### Custom Data
To use your own data, you can modify the script to include your contact list. The data should be in the following format:

```python
contacts_data = [
    {
        "phone_number": "9945194909",
        "name": "John Doe"
    },
    # Add more contacts as needed
]
```

## Features
- Generates professional-looking PDF statements
- Includes Airtel branding
- Supports custom contact names for phone numbers
- Maintains the format of the original statement
- Customizable headers and content

## File Structure
- `generate_statement.py`: Main script to generate the PDF
- `requirements.txt`: List of Python dependencies
- `README.md`: This documentation file

## Output
The script generates a PDF file named `statement.pdf` in the same directory. The PDF includes:
- Airtel branding
- Relationship and mobile numbers
- Itemized call details with names
- Formatted table with call duration, pulse, and amount # pdf-number-parser
