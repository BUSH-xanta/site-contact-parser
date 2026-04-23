# Site Contact Parser

🔎 A Python tool for extracting publicly visible contact information from websites.

This project scans websites and collects contact data that is openly available in HTML pages, such as email addresses, Telegram links or handles, and Russian mobile phone numbers. It is designed as a lightweight utility for public contact discovery, simple OSINT-style collection, and portfolio demonstration.

## 📌 Why this project

Many websites publish contact information across their homepage, contact pages, about pages, or support sections. Manually collecting this data is slow and repetitive. This tool automates the process by checking a website, exploring common contact-related pages, extracting relevant fields, and saving the results into a structured CSV file.

It is useful for:

- collecting publicly visible business contact data
- automating repetitive website review
- basic HTML parsing practice
- lightweight contact enrichment
- portfolio demonstration of practical Python scripting

## ⚙️ Features

- Normalize URLs before processing
- Remove duplicate domains
- Fallback between HTTPS and HTTP
- Extract page title as site name
- Extract email addresses
- Extract Telegram links and handles
- Extract Russian mobile phone numbers
- Check common contact-related paths
- Process a limited set of relevant internal pages
- Export structured results to CSV
- Track already processed websites
- Use a simple file-based workflow

## 🗂️ Project structure

```text
site-contact-parser/
├── .gitignore
├── LICENSE
├── README.md
├── example_sites.txt
├── requirements.txt
└── site_contact_parser.py
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

Run the parser:

```bash
python site_contact_parser.py
```

By default, the script uses these files:

- `sites.txt` - input list of raw sites
- `sites_cleaned.txt` - normalized and deduplicated sites
- `results.csv` - parsed results
- `processed_sites.txt` - already processed domains

## 📄 Output

The parser writes results to `results.csv` with the following columns:

```text
site_name
emails
telegrams
phones
url
```

Example row:

```text
Example Site,info@example.com,@example,+79991234567,https://example.com
```

## 🧠 How it works

The script follows a simple workflow:

1. Read websites from `sites.txt`
2. Normalize input URLs
3. Remove duplicate domains
4. Open the main page
5. Check common paths such as `/contacts`, `/contact`, `/about`, and `/support`
6. Extract email addresses, Telegram handles, and phone numbers
7. Save results to CSV
8. Store processed domains to avoid duplicate work later

## 📌 What the parser looks for

### Email addresses

The parser extracts standard email patterns found in visible HTML.

Examples:

```text
info@example.com
sales@example.org
hello@company.ru
```

### Telegram links and handles

The parser extracts Telegram references such as profile links and usernames.

Examples:

```text
https://t.me/example
@example
```

### Russian mobile phone numbers

The parser attempts to identify Russian mobile phone formats published on websites.

Examples:

```text
+79991234567
8 (999) 123-45-67
+7 999 123 45 67
```

## ⚠️ Limitations

This is a lightweight parser, not a full browser automation or crawling framework.

Current limitations:

- works only with publicly accessible HTML
- does not render JavaScript-heavy pages
- phone extraction is tuned mainly for Russian mobile numbers
- extraction quality depends on how the site publishes contact data
- uses a simple path-checking approach instead of deep crawling

## 🧪 Example file

The repository includes:

```text
example_sites.txt
```

This file contains a small example list of websites for testing.

## 💼 Portfolio value

This project demonstrates practical skills in:

- Python scripting
- HTTP requests and response handling
- HTML parsing with BeautifulSoup
- regex-based extraction
- CSV export
- input normalization and deduplication
- simple workflow automation
- state tracking for repeat runs

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

- add command-line arguments
- allow custom input and output file paths
- add support for deeper crawling
- add better duplicate handling for extracted contacts
- add retry and timeout tuning
- add logging and progress output
- add tests
- move the project into a `src/` package layout
- export results to JSON
- add Docker support

## 📄 License

MIT License
