from __future__ import annotations

from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .normalizers import normalize_domain, normalize_url
from .utils import is_probably_relative_url, unique_preserve_order


DEFAULT_TIMEOUT = 10.0

DEFAULT_HEADERS = {
    "User-Agent": (
        "SiteContactParser/0.2 "
        "(compatible; Python requests; publicly-visible contact extraction)"
    )
}

COMMON_CONTACT_PATHS = [
    "/contacts",
    "/contact",
    "/about",
    "/about-us",
    "/company",
    "/support",
    "/help",
    "/customer-service",
    "/feedback",
    "/team",
]


def build_session() -> requests.Session:
    """
    Create a requests session with default headers.
    """
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    return session


def is_http_url(url: str) -> bool:
    """
    Check whether a URL is HTTP or HTTPS.
    """
    lowered = url.lower()
    return lowered.startswith("http://") or lowered.startswith("https://")


def is_same_domain(base_url: str, candidate_url: str) -> bool:
    """
    Check whether two URLs belong to the same normalized domain.
    """
    return normalize_domain(base_url) == normalize_domain(candidate_url)


def build_absolute_url(base_url: str, href: str) -> str:
    """
    Convert a relative or absolute href into an absolute URL.
    """
    href = href.strip()

    if not href:
        return ""

    if not is_http_url(href):
        return urljoin(base_url, href)

    return href


def fetch_page(
    url: str,
    session: requests.Session,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, object] | None:
    """
    Fetch one page and return HTML content if the response is successful.

    Returns None for network errors, non-200 responses, or non-HTML content.
    """
    try:
        response = session.get(url, timeout=timeout)
    except requests.RequestException:
        return None

    if not response.ok:
        return None

    content_type = response.headers.get("Content-Type", "").lower()

    if "html" not in content_type and "text/plain" not in content_type:
        return None

    return {
        "url": response.url,
        "status_code": response.status_code,
        "html": response.text,
    }


def fetch_site_entry(
    raw_site: str,
    session: requests.Session,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, object] | None:
    """
    Fetch the entry page for a site with HTTPS first and HTTP fallback.
    """
    normalized = normalize_url(raw_site)

    if not normalized:
        return None

    candidates = [normalized]

    if normalized.startswith("https://"):
        http_fallback = "http://" + normalized[len("https://"):]
        candidates.append(http_fallback)

    for candidate in unique_preserve_order(candidates):
        page = fetch_page(candidate, session=session, timeout=timeout)
        if page is not None:
            page["requested_url"] = candidate
            return page

    return None


def extract_internal_links(
    base_url: str,
    html: str,
    max_links: int = 20,
) -> list[str]:
    """
    Extract candidate internal links from HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    found: list[str] = []

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()

        if not href:
            continue

        lowered = href.lower()

        if lowered.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue

        if is_probably_relative_url(href) or is_http_url(href):
            absolute_url = build_absolute_url(base_url, href)
        else:
            continue

        if not absolute_url:
            continue

        parsed = urlparse(absolute_url)

        if parsed.scheme not in {"http", "https"}:
            continue

        cleaned_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        if not is_same_domain(base_url, cleaned_url):
            continue

        found.append(cleaned_url)

    return unique_preserve_order(found)[:max_links]


def build_candidate_urls(
    base_url: str,
    html: str,
    max_internal_pages: int = 10,
) -> list[str]:
    """
    Build a list of likely useful internal URLs to check for contacts.
    """
    path_candidates = [
        urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
        for path in COMMON_CONTACT_PATHS
    ]

    discovered_links = extract_internal_links(
        base_url=base_url,
        html=html,
        max_links=max_internal_pages * 3,
    )

    prioritized_links: list[str] = []
    other_links: list[str] = []

    for link in discovered_links:
        lowered = link.lower()

        if any(keyword in lowered for keyword in ("contact", "about", "support", "help", "team", "company")):
            prioritized_links.append(link)
        else:
            other_links.append(link)

    combined = unique_preserve_order(path_candidates + prioritized_links + other_links)

    filtered = [url for url in combined if url.rstrip("/") != base_url.rstrip("/")]
    return filtered[:max_internal_pages]


def crawl_site(
    raw_site: str,
    timeout: float = DEFAULT_TIMEOUT,
    max_internal_pages: int = 10,
    session: requests.Session | None = None,
) -> dict[str, object]:
    """
    Crawl one website entry page plus a limited number of useful internal pages.

    Returns a dictionary with:
    - input_url
    - site_url
    - checked_urls
    - pages
    - success
    """
    own_session = session is None
    session = session or build_session()

    try:
        entry_page = fetch_site_entry(
            raw_site=raw_site,
            session=session,
            timeout=timeout,
        )

        if entry_page is None:
            return {
                "input_url": raw_site,
                "site_url": "",
                "checked_urls": [],
                "pages": [],
                "success": False,
            }

        site_url = str(entry_page["url"])
        checked_urls = [site_url]
        pages = [
            {
                "url": str(entry_page["url"]),
                "html": str(entry_page["html"]),
            }
        ]

        candidate_urls = build_candidate_urls(
            base_url=site_url,
            html=str(entry_page["html"]),
            max_internal_pages=max_internal_pages,
        )

        for candidate_url in candidate_urls:
            page = fetch_page(candidate_url, session=session, timeout=timeout)
            checked_urls.append(candidate_url)

            if page is None:
                continue

            final_url = str(page["url"])
            html = str(page["html"])

            if any(existing["url"] == final_url for existing in pages):
                continue

            pages.append(
                {
                    "url": final_url,
                    "html": html,
                }
            )

        return {
            "input_url": raw_site,
            "site_url": site_url,
            "checked_urls": unique_preserve_order(checked_urls),
            "pages": pages,
            "success": True,
        }
    finally:
        if own_session:
            session.close()