# Site Contact Parser

🔎 A Python tool for extracting publicly visible contact information from websites.

This project scans websites and collects contact data that is openly available in HTML pages, such as email addresses, Telegram references, and Russian mobile phone numbers. It is designed as a lightweight utility for public contact discovery, simple OSINT-style collection, and portfolio demonstration.

## 📌 Why this project

Many websites publish contact details across their homepage, contact pages, about pages, or support sections. Manually collecting this data is repetitive and slow. This tool automates the process by opening a website, checking likely contact-related pages, extracting relevant fields, and saving the results into a structured CSV file.

It is useful for:

- collecting publicly visible business contact data
- automating repetitive website review
- practicing HTML parsing and extraction logic
- lightweight contact enrichment
- portfolio demonstration of practical Python scripting

## ⚙️ Features

- normalize URLs before processing
- remove duplicate domains
- fallback from HTTPS to HTTP
- extract page title as site name
- extract email addresses
- extract Telegram links and Telegram handles in explicit Telegram context
- extract Russian mobile phone numbers
- check common contact-related paths
- process a limited number of useful internal pages
- export structured results to CSV
- track already processed websites
- support verbose logging
- include automated tests for normalization, extraction, and storage logic

## 🗂️ Project structure

```text
site-contact-parser/
├── .gitignore
├── LICENSE
├── README.md
├── example_sites.txt
├── legacy_single_file_version.py
├── requirements.txt
├── src/
│   └── site_contact_parser/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── crawler.py
│       ├── extractors.py
│       ├── normalizers.py
│       ├── storage.py
│       └── utils.py
└── tests/
    ├── test_extractors.py
    ├── test_normalizers.py
    └── test_storage.py
```

## 🧰 Requirements

- Python 3.10+
- requests
- beautifulsoup4

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/BUSH-xanta/site-contact-parser.git
cd site-contact-parser
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Optional virtual environment on Windows Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

## 🚀 Usage

Prepare a text file with one website per line.

Example input:

```text
example.com
python.org
iana.org
```

Run from the repository root:

```bash
PYTHONPATH=src python -m site_contact_parser --input example_sites.txt
```

Example with explicit output paths:

```bash
PYTHONPATH=src python -m site_contact_parser \
  --input example_sites.txt \
  --cleaned sites_cleaned.txt \
  --output results.csv \
  --processed processed_sites.txt
```

Enable verbose logging:

```bash
PYTHONPATH=src python -m site_contact_parser \
  --input example_sites.txt \
  --verbose
```

Limit the number of internal pages checked per site:

```bash
PYTHONPATH=src python -m site_contact_parser \
  --input example_sites.txt \
  --max-pages 5
```

Change HTTP timeout:

```bash
PYTHONPATH=src python -m site_contact_parser \
  --input example_sites.txt \
  --timeout 5
```

## 🖥️ Command-line arguments

```text
--input       Path to input file with one website per line
--cleaned     Path to save normalized and deduplicated sites
--output      Path to CSV output file
--processed   Path to processed domains file
--max-pages   Maximum number of internal pages to check per site
--timeout     HTTP timeout in seconds
--verbose     Enable more detailed logging output
```

## 📄 Output files

The tool writes:

- `sites_cleaned.txt` - normalized and deduplicated site list
- `results.csv` - extracted results
- `processed_sites.txt` - processed domains to avoid duplicate work on later runs

Example CSV columns:

```text
site_name
emails
telegrams
phones
url
```

Example row:

```text
Example Company,info@example.com; sales@example.com,@example_channel,+79991234567,https://example.com
```

## 🧠 How it works

The parser follows a simple workflow:

1. read websites from the input file
2. normalize and deduplicate input URLs
3. fetch the main page with HTTPS first and HTTP fallback
4. check common contact-related paths such as `/contacts`, `/contact`, `/about`, and `/support`
5. extract emails, Telegram references, and phone numbers from HTML
6. normalize and deduplicate extracted values
7. save results to CSV
8. store processed domains to avoid duplicate work later

## 📌 What the parser looks for

### Email addresses

The parser extracts standard email patterns found in visible HTML and `mailto:` links.

Examples:

```text
info@example.com
sales@example.org
hello@company.ru
```

### Telegram references

The parser extracts:

- explicit Telegram links such as `https://t.me/example`
- Telegram handles in explicit Telegram context such as `Telegram: @example`

Examples:

```text
https://t.me/example
Telegram: @example
```

### Russian mobile phone numbers

The parser attempts to identify Russian mobile phone formats in visible HTML text and `tel:` links.

Examples:

```text
+79991234567
8 (999) 123-45-67
+7 999 123 45 67
```

## 🧪 Tests

Run all tests from the repository root:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

The current test suite covers:

- normalization helpers
- contact extraction logic
- storage helpers

## ⚠️ Limitations

This is a lightweight parser, not a full crawler or browser automation framework.

Current limitations:

- works only with publicly accessible HTML
- does not render JavaScript-heavy pages
- phone extraction is tuned mainly for Russian mobile numbers
- extraction quality depends on how the site publishes contact data
- uses a limited internal page discovery strategy instead of deep crawling
- does not yet include retry tuning or advanced crawl rules

## 💼 Portfolio value

This project demonstrates practical skills in:

- Python scripting
- HTTP requests and response handling
- HTML parsing with BeautifulSoup
- regex-based extraction
- normalization and deduplication
- CSV export
- modular project structure with `src/` layout
- command-line interface design
- logging and progress output
- automated testing with `unittest`

## ✅ Responsible use

Use this tool only for lawful and legitimate purposes.

Respect:

- website terms of service
- rate limits where applicable
- privacy and local law
- responsible collection and use of publicly visible data

This project is intended for working with contact information that websites openly publish. It is not designed for bypassing access controls, scraping private content, or interacting with restricted areas.

## 🔮 Future improvements

Possible next steps:

- add retry and timeout tuning
- support deeper crawling
- export results to JSON
- add Docker support
- add tests for CLI behavior

## 📄 License

MIT License