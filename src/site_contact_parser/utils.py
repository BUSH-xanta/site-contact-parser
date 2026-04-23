from __future__ import annotations

from collections.abc import Iterable


def clean_whitespace(value: str) -> str:
    """
    Collapse repeated whitespace into single spaces and strip edges.

    Example:
        "  Hello   world \n test  " -> "Hello world test"
    """
    return " ".join(value.split())


def unique_preserve_order(values: Iterable[str]) -> list[str]:
    """
    Return unique strings while preserving original order.

    Example:
        ["a", "b", "a", "c"] -> ["a", "b", "c"]
    """
    seen: set[str] = set()
    result: list[str] = []

    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)

    return result


def join_unique(values: Iterable[str], separator: str = "; ") -> str:
    """
    Join unique values into one string.

    Example:
        ["a", "b", "a"] -> "a; b"
    """
    cleaned_values = [clean_whitespace(value) for value in values if clean_whitespace(value)]
    return separator.join(unique_preserve_order(cleaned_values))


def ensure_list(value: str | Iterable[str] | None) -> list[str]:
    """
    Convert input into a list of strings.

    Example:
        "abc" -> ["abc"]
        ["a", "b"] -> ["a", "b"]
        None -> []
    """
    if value is None:
        return []

    if isinstance(value, str):
        return [value]

    return [item for item in value]


def is_probably_relative_url(url: str) -> bool:
    """
    Check whether a URL looks relative rather than absolute.

    Examples:
        "/contacts" -> True
        "contacts" -> True
        "https://example.com" -> False
    """
    url_lower = url.lower()

    return not (
        url_lower.startswith("http://")
        or url_lower.startswith("https://")
        or url_lower.startswith("mailto:")
        or url_lower.startswith("tel:")
        or url_lower.startswith("javascript:")
        or url_lower.startswith("#")
    )