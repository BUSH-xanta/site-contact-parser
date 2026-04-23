import csv
import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

TIMEOUT = 12
DELAY_BETWEEN_SITES = 1.0
MAX_EXTRA_INTERNAL_PAGES = 8

INPUT_FILE = "sites.txt"
CLEANED_INPUT_FILE = "sites_cleaned.txt"
RESULTS_FILE = "results.csv"
PROCESSED_FILE = "processed_sites.txt"

CONTACT_PATHS = [
    "/",
    "/contacts",
    "/contact",
    "/kontakty",
    "/kontakt",
    "/about",
    "/about-us",
    "/company",
    "/support",
    "/feedback",
]

CONTACT_KEYWORDS = [
    "contact", "contacts", "kontakt", "kontakty", "about", "company", "support",
    "контакт", "контакты", "о нас", "компания", "поддержка", "обратная связь"
]

EMAIL_REGEX = re.compile(
    r"(?i)(?:mailto:)?([a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,})"
)

TG_LINK_REGEX = re.compile(
    r"(?i)https?://(?:t\.me|telegram\.me|telegram\.dog)/([A-Za-z0-9_]{4,})"
)

TG_HANDLE_REGEX = re.compile(
    r"(?<![\w@])@([A-Za-z0-9_]{5,32})"
)

PHONE_REGEX = re.compile(
    r"(?:\+7|8|7)?[\s\-\(\)]*9\d(?:[\s\-\(\)]*\d){8}"
)

BAD_TG_WORDS = {
    "gmail", "mail", "email", "admin", "info", "support", "manager",
    "example", "yandex", "inbox", "login", "telegram", "channel"
}


def strip_tracking_params(url):
    url = url.strip()
    if not url:
        return ""

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)

    scheme = parsed.scheme.lower() if parsed.scheme else "https"
    netloc = parsed.netloc.lower().strip()
    path = parsed.path.strip()

    if netloc.startswith("www."):
        netloc_no_www = netloc[4:]
    else:
        netloc_no_www = netloc

    if not path:
        path = "/"

    cleaned = f"{scheme}://{netloc_no_www}{path}"

    if cleaned.endswith("/") and path != "/":
        cleaned = cleaned.rstrip("/")

    return cleaned


def normalize_input_url(url):
    return strip_tracking_params(url)


def get_base_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def get_domain(url):
    normalized = normalize_input_url(url)
    if not normalized:
        return ""

    parsed = urlparse(normalized)
    domain = parsed.netloc.lower().strip()

    if domain.startswith("www."):
        domain = domain[4:]

    return domain


def safe_request(url):
    try_urls = [url]

    parsed = urlparse(url)
    if parsed.scheme == "https":
        try_urls.append("http://" + parsed.netloc + parsed.path)
    elif parsed.scheme == "http":
        try_urls.append("https://" + parsed.netloc + parsed.path)

    tried = set()

    for candidate in try_urls:
        if candidate in tried:
            continue
        tried.add(candidate)

        try:
            response = requests.get(
                candidate,
                headers=HEADERS,
                timeout=TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()
            response.encoding = response.apparent_encoding or response.encoding
            return response.text
        except requests.RequestException:
            continue

    return ""


def extract_title(html, fallback):
    if not html:
        return fallback

    soup = BeautifulSoup(html, "html.parser")

    if soup.title and soup.title.get_text(strip=True):
        return soup.title.get_text(" ", strip=True)

    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content"):
        return og_title["content"].strip()

    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(" ", strip=True)

    return fallback


def clean_email(email):
    email = email.strip().lower()
    if email.startswith("mailto:"):
        email = email[7:]
    return email.strip(" .,:;!?()[]{}<>\"'")


def extract_emails(text, html):
    found = set()

    for source in (text, html):
        if not source:
            continue
        for match in EMAIL_REGEX.findall(source):
            email = clean_email(match)
            if email and not email.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".svg", ".gif", ".avif")):
                found.add(email)

    return sorted(found)


def clean_tg_handle(handle):
    handle = handle.strip().lstrip("@")
    return handle.strip(" .,:;!?()[]{}<>\"'/\\")


def extract_telegrams(html, text):
    found = set()

    if html:
        for handle in TG_LINK_REGEX.findall(html):
            handle = clean_tg_handle(handle)
            if handle and handle.lower() not in BAD_TG_WORDS:
                found.add("@" + handle)

    if text:
        for handle in TG_HANDLE_REGEX.findall(text):
            handle = clean_tg_handle(handle)
            if handle and handle.lower() not in BAD_TG_WORDS:
                found.add("@" + handle)

    return sorted(found)


def is_fake_mobile(phone):
    bad_numbers = {
        "+79999999999",
        "+79000000000",
        "+79111111111",
        "+79222222222",
        "+79333333333",
        "+79444444444",
        "+79555555555",
        "+79666666666",
        "+79777777777",
        "+79888888888",
    }

    if phone in bad_numbers:
        return True

    digits = phone[1:]

    if len(set(digits)) == 1:
        return True

    if digits[-10:] in {
        "0000000000",
        "1111111111",
        "2222222222",
        "3333333333",
        "4444444444",
        "5555555555",
        "6666666666",
        "7777777777",
        "8888888888",
        "9999999999",
        "1234567890",
        "0123456789",
    }:
        return True

    return False


def normalize_phone(phone):
    phone = phone.strip()
    if not phone:
        return ""

    digits = re.sub(r"\D", "", phone)

    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    elif len(digits) == 11 and digits.startswith("7"):
        pass
    else:
        return ""

    normalized = "+" + digits

    if not re.fullmatch(r"\+79\d{9}", normalized):
        return ""

    if is_fake_mobile(normalized):
        return ""

    return normalized


def extract_phones(text, html):
    found = set()

    for source in (html, text):
        if not source:
            continue

        for raw in PHONE_REGEX.findall(source):
            phone = normalize_phone(raw)
            if phone:
                found.add(phone)

    return sorted(found)


def collect_candidate_links(base_url, html):
    soup = BeautifulSoup(html, "html.parser")
    results = set()
    base_netloc = urlparse(base_url).netloc

    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        text = a.get_text(" ", strip=True).lower()
        href_lower = href.lower()

        if not href:
            continue

        if any(keyword in text for keyword in CONTACT_KEYWORDS) or any(keyword in href_lower for keyword in CONTACT_KEYWORDS):
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)

            if parsed.netloc == base_netloc:
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if clean_url.endswith("/") and parsed.path != "/":
                    clean_url = clean_url.rstrip("/")
                results.add(clean_url)

    return sorted(results)


def html_to_text(html):
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text("\n", strip=True)


def parse_site(url):
    normalized = normalize_input_url(url)
    if not normalized:
        return {
            "site_name": "Не найдено",
            "emails": [],
            "telegrams": [],
            "phones": [],
            "url": url
        }

    base_url = get_base_url(normalized)
    main_html = safe_request(base_url)

    pages_to_check = []
    seen_pages = set()

    for path in CONTACT_PATHS:
        page = urljoin(base_url, path)
        if page not in seen_pages:
            seen_pages.add(page)
            pages_to_check.append(page)

    if main_html:
        extra_links = collect_candidate_links(base_url, main_html)
        for link in extra_links[:MAX_EXTRA_INTERNAL_PAGES]:
            if link not in seen_pages:
                seen_pages.add(link)
                pages_to_check.append(link)

    all_html_parts = []
    site_title = extract_title(main_html, base_url)

    for page_url in pages_to_check:
        html = main_html if page_url == base_url and main_html else safe_request(page_url)
        if html:
            all_html_parts.append(html)

    combined_html = "\n".join(all_html_parts)
    combined_text = html_to_text(combined_html)

    emails = extract_emails(combined_text, combined_html)
    telegrams = extract_telegrams(combined_html, combined_text)
    phones = extract_phones(combined_text, combined_html)

    return {
        "site_name": site_title,
        "emails": emails,
        "telegrams": telegrams,
        "phones": phones,
        "url": base_url
    }


def read_sites_from_file(file_path=INPUT_FILE):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return []


def read_sites_from_input():
    print("Файл sites.txt не найден или пуст.")
    print("Вставь один или несколько сайтов через запятую.")
    print("Пример: example.com, openai.com, telegram.org")
    raw = input("Сайты: ").strip()

    if not raw:
        return []

    parts = [item.strip() for item in raw.split(",")]
    return [item for item in parts if item]


def clean_and_dedupe_sites(raw_sites):
    unique_domains = set()
    cleaned_sites = []

    for site in raw_sites:
        cleaned = normalize_input_url(site)
        if not cleaned:
            continue

        domain = get_domain(cleaned)
        if not domain:
            continue

        if domain in unique_domains:
            continue

        unique_domains.add(domain)
        cleaned_sites.append(cleaned)

    return cleaned_sites


def save_cleaned_sites(sites, file_path=CLEANED_INPUT_FILE):
    with open(file_path, "w", encoding="utf-8") as file:
        for site in sites:
            file.write(site + "\n")


def load_processed_sites(file_path=PROCESSED_FILE):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return {line.strip().lower() for line in file if line.strip()}
    except FileNotFoundError:
        return set()


def append_processed_site(domain, file_path=PROCESSED_FILE):
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(domain + "\n")


def load_existing_result_domains(file_path=RESULTS_FILE):
    existing = set()

    try:
        with open(file_path, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                url = row.get("url", "").strip()
                domain = get_domain(url)
                if domain:
                    existing.add(domain)
    except FileNotFoundError:
        pass

    return existing


def append_result_to_csv(row, output_file=RESULTS_FILE):
    file_exists = False

    try:
        with open(output_file, "r", encoding="utf-8-sig"):
            file_exists = True
    except FileNotFoundError:
        file_exists = False

    with open(output_file, "a", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["site_name", "emails", "telegrams", "phones", "url"]
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "site_name": row["site_name"],
            "emails": ", ".join(row["emails"]) if row["emails"] else "",
            "telegrams": ", ".join(row["telegrams"]) if row["telegrams"] else "",
            "phones": ", ".join(row["phones"]) if row["phones"] else "",
            "url": row["url"]
        })


def main():
    raw_sites = read_sites_from_file(INPUT_FILE)

    if not raw_sites:
        raw_sites = read_sites_from_input()

    if not raw_sites:
        print("Список сайтов пуст.")
        return

    cleaned_sites = clean_and_dedupe_sites(raw_sites)
    save_cleaned_sites(cleaned_sites, CLEANED_INPUT_FILE)

    processed_sites = load_processed_sites(PROCESSED_FILE)
    result_domains = load_existing_result_domains(RESULTS_FILE)

    total = len(cleaned_sites)
    skipped = 0
    added = 0

    for index, site in enumerate(cleaned_sites, start=1):
        domain = get_domain(site)

        if not domain:
            print(f"[{index}/{total}] Пропускаю некорректный ввод: {site}")
            skipped += 1
            continue

        if domain in processed_sites or domain in result_domains:
            print(f"[{index}/{total}] Уже был обработан, пропускаю: {domain}")
            skipped += 1
            continue

        print(f"[{index}/{total}] Обрабатываю: {domain}")

        data = parse_site(site)
        append_result_to_csv(data, RESULTS_FILE)
        append_processed_site(domain, PROCESSED_FILE)

        processed_sites.add(domain)
        result_domains.add(domain)
        added += 1

        time.sleep(DELAY_BETWEEN_SITES)

    print("\nГотово.")
    print(f"Очищенный список сайтов: {CLEANED_INPUT_FILE}")
    print(f"Новых сайтов обработано: {added}")
    print(f"Пропущено: {skipped}")
    print(f"Результаты: {RESULTS_FILE}")
    print(f"Память обработанных сайтов: {PROCESSED_FILE}")


if __name__ == "__main__":
    main()