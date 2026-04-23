from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Sequence

from .crawler import crawl_site
from .extractors import extract_contacts_from_html
from .normalizers import normalize_domain, normalize_url
from .storage import (
    append_processed_domain,
    append_result_row,
    build_result_row,
    load_processed_domains,
    load_text_lines,
    save_cleaned_sites,
)
from .utils import unique_preserve_order


LOGGER = logging.getLogger("site_contact_parser")


def configure_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract publicly visible contact data from websites."
    )

    parser.add_argument(
        "--input",
        default="sites.txt",
        help="Path to input file with one website per line. Default: sites.txt",
    )
    parser.add_argument(
        "--cleaned",
        default="sites_cleaned.txt",
        help="Path to save normalized and deduplicated sites. Default: sites_cleaned.txt",
    )
    parser.add_argument(
        "--output",
        default="results.csv",
        help="Path to CSV output file. Default: results.csv",
    )
    parser.add_argument(
        "--processed",
        default="processed_sites.txt",
        help="Path to processed domains file. Default: processed_sites.txt",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Maximum number of internal pages to check per site. Default: 10",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP timeout in seconds. Default: 10.0",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable more detailed logging output.",
    )

    return parser


def load_and_normalize_sites(input_path: Path) -> list[str]:
    raw_sites = load_text_lines(input_path, allow_missing=False)

    normalized_sites: list[str] = []

    for raw_site in raw_sites:
        normalized = normalize_url(raw_site)
        if normalized:
            normalized_sites.append(normalized)

    return unique_preserve_order(normalized_sites)


def collect_contacts_from_pages(pages: list[dict[str, str]]) -> dict[str, list[str] | str]:
    site_name = ""
    emails: list[str] = []
    telegrams: list[str] = []
    phones: list[str] = []

    for page in pages:
        html = page["html"]
        extracted = extract_contacts_from_html(html)

        if not site_name and extracted["site_name"]:
            site_name = str(extracted["site_name"])

        emails.extend(str(item) for item in extracted["emails"])
        telegrams.extend(str(item) for item in extracted["telegrams"])
        phones.extend(str(item) for item in extracted["phones"])

    return {
        "site_name": site_name,
        "emails": emails,
        "telegrams": telegrams,
        "phones": phones,
    }


def handle_site(
    site: str,
    output_path: Path,
    processed_path: Path,
    timeout: float,
    max_pages: int,
) -> bool:
    LOGGER.debug("Starting crawl for site: %s", site)

    crawl_result = crawl_site(
        raw_site=site,
        timeout=timeout,
        max_internal_pages=max_pages,
    )

    append_processed_domain(processed_path, site)

    if not crawl_result["success"]:
        LOGGER.warning("Failed to fetch site: %s", site)
        return False

    pages = crawl_result["pages"]
    LOGGER.debug(
        "Fetched %s page(s) for %s",
        len(pages),
        site,
    )

    contacts = collect_contacts_from_pages(pages)

    row = build_result_row(
        site_name=str(contacts["site_name"]),
        emails=[str(item) for item in contacts["emails"]],
        telegrams=[str(item) for item in contacts["telegrams"]],
        phones=[str(item) for item in contacts["phones"]],
        url=str(crawl_result["site_url"]),
    )

    append_result_row(output_path, row)

    LOGGER.info(
        "Saved result for %s - emails: %s, telegrams: %s, phones: %s",
        site,
        len([item for item in contacts["emails"] if str(item)]),
        len([item for item in contacts["telegrams"] if str(item)]),
        len([item for item in contacts["phones"] if str(item)]),
    )

    return True


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    configure_logging(verbose=args.verbose)

    input_path = Path(args.input)
    cleaned_path = Path(args.cleaned)
    output_path = Path(args.output)
    processed_path = Path(args.processed)

    if args.max_pages < 1:
        LOGGER.error("--max-pages must be greater than 0")
        return 1

    if args.timeout <= 0:
        LOGGER.error("--timeout must be greater than 0")
        return 1

    try:
        sites = load_and_normalize_sites(input_path)
    except FileNotFoundError:
        LOGGER.error("Input file does not exist: %s", input_path)
        return 1

    if not sites:
        LOGGER.info("No valid sites found in input file.")
        return 0

    LOGGER.info("Loaded %s normalized site(s)", len(sites))
    save_cleaned_sites(cleaned_path, sites)
    LOGGER.info("Saved cleaned site list to %s", cleaned_path)

    processed_domains = load_processed_domains(processed_path)
    LOGGER.info("Loaded %s processed domain(s)", len(processed_domains))

    total_sites = len(sites)
    skipped_sites = 0
    success_sites = 0
    failed_sites = 0

    for index, site in enumerate(sites, start=1):
        domain = normalize_domain(site)

        if domain in processed_domains:
            skipped_sites += 1
            LOGGER.info("[%s/%s] Skipping already processed site: %s", index, total_sites, site)
            continue

        LOGGER.info("[%s/%s] Processing: %s", index, total_sites, site)

        success = handle_site(
            site=site,
            output_path=output_path,
            processed_path=processed_path,
            timeout=args.timeout,
            max_pages=args.max_pages,
        )

        if success:
            success_sites += 1
        else:
            failed_sites += 1

    LOGGER.info("Done.")
    LOGGER.info("Total sites: %s", total_sites)
    LOGGER.info("Processed successfully: %s", success_sites)
    LOGGER.info("Skipped: %s", skipped_sites)
    LOGGER.info("Failed: %s", failed_sites)
    LOGGER.info("Cleaned sites file: %s", cleaned_path)
    LOGGER.info("CSV output file: %s", output_path)
    LOGGER.info("Processed domains file: %s", processed_path)

    return 0