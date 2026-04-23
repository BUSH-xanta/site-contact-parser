from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from .normalizers import (
    deduplicate_emails,
    deduplicate_phones,
    deduplicate_telegrams,
    normalize_domain,
)
from .utils import clean_whitespace, join_unique, unique_preserve_order


RESULT_FIELDNAMES = [
    "site_name",
    "emails",
    "telegrams",
    "phones",
    "url",
]


def ensure_parent_directory(path: Path) -> None:
    """
    Create parent directory if it does not exist.
    """
    path.parent.mkdir(parents=True, exist_ok=True)


def load_text_lines(path: Path, allow_missing: bool = True) -> list[str]:
    """
    Read non-empty stripped lines from a text file.

    If allow_missing is True and the file does not exist, return an empty list.
    """
    if not path.exists():
        if allow_missing:
            return []
        raise FileNotFoundError(f"File does not exist: {path}")

    with path.open("r", encoding="utf-8", errors="replace") as file:
        lines = [line.strip() for line in file if line.strip()]

    return lines


def save_text_lines(path: Path, lines: Iterable[str]) -> None:
    """
    Save lines to a text file, one value per line.
    """
    ensure_parent_directory(path)

    cleaned_lines = [
        clean_whitespace(line)
        for line in lines
        if clean_whitespace(line)
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        for line in cleaned_lines:
            file.write(f"{line}\n")


def load_processed_domains(path: Path) -> set[str]:
    """
    Load processed domains from a text file.
    """
    lines = load_text_lines(path, allow_missing=True)

    result: set[str] = set()

    for line in lines:
        domain = normalize_domain(line)
        if domain:
            result.add(domain)

    return result


def append_processed_domain(path: Path, raw_value: str) -> None:
    """
    Append one normalized processed domain to a text file.

    If the value cannot be normalized, nothing is written.
    """
    domain = normalize_domain(raw_value)

    if not domain:
        return

    ensure_parent_directory(path)

    with path.open("a", encoding="utf-8", newline="") as file:
        file.write(f"{domain}\n")


def save_cleaned_sites(path: Path, sites: Iterable[str]) -> None:
    """
    Save cleaned site values to a text file with deduplication and preserved order.
    """
    cleaned_sites = [
        clean_whitespace(site)
        for site in sites
        if clean_whitespace(site)
    ]

    save_text_lines(path, unique_preserve_order(cleaned_sites))


def build_result_row(
    site_name: str,
    emails: Iterable[str],
    telegrams: Iterable[str],
    phones: Iterable[str],
    url: str,
) -> dict[str, str]:
    """
    Build one normalized CSV row for extracted contact data.
    """
    deduplicated_emails = deduplicate_emails(emails)
    deduplicated_telegrams = deduplicate_telegrams(telegrams)
    deduplicated_phones = deduplicate_phones(phones)

    return {
        "site_name": clean_whitespace(site_name),
        "emails": join_unique(deduplicated_emails),
        "telegrams": join_unique(deduplicated_telegrams),
        "phones": join_unique(deduplicated_phones),
        "url": clean_whitespace(url),
    }


def append_result_row(output_path: Path, row: dict[str, str]) -> None:
    """
    Append one result row to the CSV file and write header if needed.
    """
    ensure_parent_directory(output_path)

    file_exists = output_path.exists()
    file_has_content = file_exists and output_path.stat().st_size > 0

    with output_path.open("a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=RESULT_FIELDNAMES)

        if not file_has_content:
            writer.writeheader()

        writer.writerow(row)


def load_existing_result_urls(path: Path) -> set[str]:
    """
    Load already saved result URLs from an existing CSV file.

    If the file does not exist, return an empty set.
    """
    if not path.exists():
        return set()

    result: set[str] = set()

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            url = clean_whitespace(row.get("url", ""))
            if url:
                result.add(url)

    return result