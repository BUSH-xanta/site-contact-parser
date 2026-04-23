from __future__ import annotations

import re
from bs4 import BeautifulSoup

from .normalizers import (
    deduplicate_emails,
    deduplicate_phones,
    deduplicate_telegrams,
    normalize_email,
    normalize_phone,
    normalize_site_name,
    normalize_telegram,
)


EMAIL_REGEX = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

TELEGRAM_LINK_REGEX = re.compile(
    r"https?://(?:www\.)?(?:t\.me|telegram\.me)/([A-Za-z0-9_]{3,32})/?",
    re.IGNORECASE,
)

TELEGRAM_HANDLE_REGEX = re.compile(
    r"(?<![\w.])@([A-Za-z][A-Za-z0-9_]{2,31})\b"
)

RUSSIAN_MOBILE_PHONE_REGEX = re.compile(
    r"(?:(?:\+7|8)\s*\(?\s*9\d{2}\s*\)?[\s-]*\d{3}[\s-]*\d{2}[\s-]*\d{2})"
)


def extract_site_name_from_html(html: str) -> str:
    """
    Extract and normalize page title from HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")

    if title_tag is None:
        return ""

    return normalize_site_name(title_tag.get_text(" ", strip=True))


def extract_emails_from_text(text: str) -> list[str]:
    """
    Extract email addresses from plain text.
    """
    matches = EMAIL_REGEX.findall(text)
    normalized = [normalize_email(match) for match in matches]
    return deduplicate_emails(normalized)


def extract_telegrams_from_text(text: str) -> list[str]:
    """
    Extract Telegram links and @handles from plain text.
    """
    found: list[str] = []

    for username in TELEGRAM_LINK_REGEX.findall(text):
        telegram = normalize_telegram(f"@{username}")
        if telegram:
            found.append(telegram)

    for username in TELEGRAM_HANDLE_REGEX.findall(text):
        telegram = normalize_telegram(f"@{username}")
        if telegram:
            found.append(telegram)

    return deduplicate_telegrams(found)


def extract_phones_from_text(text: str) -> list[str]:
    """
    Extract Russian mobile phone numbers from plain text.
    """
    matches = RUSSIAN_MOBILE_PHONE_REGEX.findall(text)
    normalized = [normalize_phone(match) for match in matches]
    return deduplicate_phones(normalized)


def extract_emails_from_html(html: str) -> list[str]:
    """
    Extract emails from visible HTML text and mailto links.
    """
    soup = BeautifulSoup(html, "html.parser")
    found: list[str] = []

    text = soup.get_text(" ", strip=True)
    found.extend(extract_emails_from_text(text))

    for link in soup.find_all("a", href=True):
        href = link["href"].strip()

        if href.lower().startswith("mailto:"):
            email = normalize_email(href[7:])
            if email:
                found.append(email)

    return deduplicate_emails(found)


def extract_telegrams_from_html(html: str) -> list[str]:
    """
    Extract Telegram handles from visible HTML text and Telegram links.
    """
    soup = BeautifulSoup(html, "html.parser")
    found: list[str] = []

    text = soup.get_text(" ", strip=True)
    found.extend(extract_telegrams_from_text(text))

    for link in soup.find_all("a", href=True):
        href = link["href"].strip()

        telegram = normalize_telegram(href)
        if telegram:
            found.append(telegram)

    return deduplicate_telegrams(found)


def extract_phones_from_html(html: str) -> list[str]:
    """
    Extract phone numbers from visible HTML text and tel links.
    """
    soup = BeautifulSoup(html, "html.parser")
    found: list[str] = []

    text = soup.get_text(" ", strip=True)
    found.extend(extract_phones_from_text(text))

    for link in soup.find_all("a", href=True):
        href = link["href"].strip()

        if href.lower().startswith("tel:"):
            phone = normalize_phone(href[4:])
            if phone:
                found.append(phone)

    return deduplicate_phones(found)


def extract_contacts_from_html(html: str) -> dict[str, list[str] | str]:
    """
    Extract site title, emails, Telegram handles, and phones from HTML.
    """
    return {
        "site_name": extract_site_name_from_html(html),
        "emails": extract_emails_from_html(html),
        "telegrams": extract_telegrams_from_html(html),
        "phones": extract_phones_from_html(html),
    }