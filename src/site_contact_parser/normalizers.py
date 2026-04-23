from __future__ import annotations

import re
from urllib.parse import urlparse


TELEGRAM_HOSTS = {
    "t.me",
    "www.t.me",
    "telegram.me",
    "www.telegram.me",
}


def normalize_url(raw_url: str) -> str:
    """
    Normalize a raw website value into a usable URL string.

    Examples:
        "example.com" -> "https://example.com"
        " HTTPS://Example.com/path " -> "https://example.com/path"
    """
    value = raw_url.strip()

    if not value:
        return ""

    if not value.startswith(("http://", "https://")):
        value = f"https://{value}"

    parsed = urlparse(value)

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or ""

    if path == "/":
        path = ""

    return f"{scheme}://{netloc}{path}"


def normalize_domain(raw_url: str) -> str:
    """
    Extract and normalize the domain from a raw URL-like value.

    Examples:
        "example.com" -> "example.com"
        "https://WWW.Example.com/test" -> "www.example.com"
    """
    normalized_url = normalize_url(raw_url)

    if not normalized_url:
        return ""

    parsed = urlparse(normalized_url)
    return parsed.netloc.lower()


def normalize_email(email: str) -> str:
    """
    Normalize email to lowercase and trim punctuation around it.
    """
    value = email.strip().strip(".,;:()[]{}<>\"'").lower()
    return value


def normalize_telegram(value: str) -> str:
    """
    Normalize Telegram handle or link to '@username' form.

    Examples:
        "@example" -> "@example"
        "https://t.me/example" -> "@example"
        "t.me/example/" -> "@example"
    """
    raw = value.strip()

    if not raw:
        return ""

    raw = raw.strip(".,;:()[]{}<>\"'")

    if raw.startswith("@"):
        username = raw[1:]
    else:
        lowered = raw.lower()

        if lowered.startswith(("http://", "https://")):
            parsed = urlparse(raw)
            if parsed.netloc.lower() not in TELEGRAM_HOSTS:
                return ""
            username = parsed.path.strip("/")
        elif lowered.startswith(("t.me/", "telegram.me/")):
            username = raw.split("/", 1)[1].strip("/")
        else:
            username = raw

    username = username.strip().lstrip("@").strip("/")
    username = re.sub(r"[^\w]", "", username)

    if not username:
        return ""

    return f"@{username}"


def normalize_phone(phone: str) -> str:
    """
    Normalize Russian phone number to '+7XXXXXXXXXX' format when possible.

    Examples:
        "+7 999 123 45 67" -> "+79991234567"
        "8 (999) 123-45-67" -> "+79991234567"
    """
    digits = re.sub(r"\D", "", phone)

    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]

    if len(digits) == 11 and digits.startswith("7"):
        return f"+{digits}"

    return ""


def normalize_site_name(title: str) -> str:
    """
    Clean and normalize page title for CSV output.
    """
    value = " ".join(title.split()).strip()
    return value