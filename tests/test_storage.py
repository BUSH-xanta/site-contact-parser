import csv
import tempfile
import unittest
from pathlib import Path

from site_contact_parser.storage import (
    append_processed_domain,
    append_result_row,
    build_result_row,
    load_existing_result_urls,
    load_processed_domains,
    load_text_lines,
    save_cleaned_sites,
)


class TestStorage(unittest.TestCase):
    def test_build_result_row_normalizes_and_deduplicates_contacts(self) -> None:
        row = build_result_row(
            site_name="  Example   Company  ",
            emails=["INFO@example.com", "info@example.com", "sales@example.com"],
            telegrams=["@Example", "https://t.me/example", "@sales_team"],
            phones=["+7 999 123 45 67", "8 (999) 123-45-67", "+7 912 000 11 22"],
            url="  https://example.com  ",
        )

        self.assertEqual(row["site_name"], "Example Company")
        self.assertEqual(row["emails"], "info@example.com; sales@example.com")
        self.assertEqual(row["telegrams"], "@example; @sales_team")
        self.assertEqual(row["phones"], "+79991234567; +79120001122")
        self.assertEqual(row["url"], "https://example.com")

    def test_save_cleaned_sites_deduplicates_and_preserves_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "sites_cleaned.txt"

            save_cleaned_sites(
                path,
                [
                    " https://example.com ",
                    "https://example.com",
                    "https://iana.org",
                    "https://python.org",
                    "https://iana.org",
                ],
            )

            lines = load_text_lines(path, allow_missing=False)

            self.assertEqual(
                lines,
                [
                    "https://example.com",
                    "https://iana.org",
                    "https://python.org",
                ],
            )

    def test_append_processed_domain_and_load_processed_domains(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "processed_sites.txt"

            append_processed_domain(path, "https://Example.com/test")
            append_processed_domain(path, "example.com")
            append_processed_domain(path, "https://iana.org")

            domains = load_processed_domains(path)

            self.assertEqual(domains, {"example.com", "iana.org"})

    def test_append_result_row_writes_header_and_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "results.csv"

            row1 = build_result_row(
                site_name="Example",
                emails=["info@example.com"],
                telegrams=["@example"],
                phones=["+79991234567"],
                url="https://example.com",
            )

            row2 = build_result_row(
                site_name="IANA",
                emails=["admin@iana.org"],
                telegrams=[],
                phones=[],
                url="https://iana.org",
            )

            append_result_row(path, row1)
            append_result_row(path, row2)

            with path.open("r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)
                rows = list(reader)

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["site_name"], "Example")
            self.assertEqual(rows[0]["emails"], "info@example.com")
            self.assertEqual(rows[1]["site_name"], "IANA")
            self.assertEqual(rows[1]["url"], "https://iana.org")

    def test_load_existing_result_urls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "results.csv"

            row1 = build_result_row(
                site_name="Example",
                emails=["info@example.com"],
                telegrams=[],
                phones=[],
                url="https://example.com",
            )

            row2 = build_result_row(
                site_name="Python",
                emails=["hello@python.org"],
                telegrams=[],
                phones=[],
                url="https://python.org",
            )

            append_result_row(path, row1)
            append_result_row(path, row2)

            urls = load_existing_result_urls(path)

            self.assertEqual(
                urls,
                {"https://example.com", "https://python.org"},
            )


if __name__ == "__main__":
    unittest.main()