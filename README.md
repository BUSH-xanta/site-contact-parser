# Site Contact Parser

Python parser for extracting publicly visible contact data from websites.

The script scans a website and tries to collect:

- email addresses
- Telegram links and handles
- Russian mobile phone numbers

It checks the main page, common contact-related paths, and a limited number of internal pages that look like contact pages.

## Features

- URL normalization before processing
- duplicate domain removal
- fallback between HTTPS and HTTP
- extraction of page title as site name
- parsing of emails, Telegram handles, and phone numbers
- CSV export
- tracking of already processed sites

## Project Structure

site-contact-parser/
- site_contact_parser.py
- requirements.txt
- .gitignore
- README.md
- LICENSE
- example_sites.txt

## Requirements

- Python 3.10+
- requests
- beautifulsoup4

## Installation

Clone the repository:

    git clone https://github.com/BUSH-xanta/site-contact-parser.git
    cd site-contact-parser

Install dependencies:

    pip install -r requirements.txt

Optional virtual environment on Windows Git Bash:

    python -m venv .venv
    source .venv/Scripts/activate
    pip install -r requirements.txt

## Usage

Prepare a text file with one website per line.

Example sites.txt:

    example.com
    python.org
    iana.org

Run the parser:

    python site_contact_parser.py

By default, the script uses these files:

- sites.txt - input list of raw sites
- sites_cleaned.txt - normalized and deduplicated sites
- results.csv - parsed results
- processed_sites.txt - already processed domains

## Output

The parser writes results to results.csv with the following columns:

- site_name
- emails
- telegrams
- phones
- url

Example row:

    site_name,emails,telegrams,phones,url
    Example Site,info@example.com,@example,+79991234567,https://example.com

## How It Works

1. Reads websites from sites.txt
2. Normalizes input URLs
3. Removes duplicate domains
4. Opens the main page
5. Checks common contact pages such as /contacts, /contact, /about, /support
6. Extracts emails, Telegram handles, and phone numbers
7. Saves results to CSV
8. Stores processed domains to avoid duplicate work

## Notes

- The parser only works with publicly accessible HTML content.
- It does not render JavaScript-heavy pages in a browser.
- Phone number extraction is tuned for Russian mobile numbers.
- Extraction quality depends on how the website publishes contact data.

## Example Files

example_sites.txt contains a small example input list for testing.

## Responsible Use

Use this tool only for lawful and legitimate purposes.

Respect:

- website terms of service
- rate limits where applicable
- privacy and local law
- responsible collection and use of publicly visible data

## License

MIT License
