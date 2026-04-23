import unittest

from site_contact_parser.normalizers import (
    deduplicate_emails,
    deduplicate_phones,
    deduplicate_telegrams,
    normalize_domain,
    normalize_email,
    normalize_phone,
    normalize_telegram,
    normalize_url,
)


class TestNormalizers(unittest.TestCase):
    def test_normalize_url_adds_https(self) -> None:
        self.assertEqual(
            normalize_url("example.com"),
            "https://example.com",
        )

    def test_normalize_url_lowercases_scheme_and_domain(self) -> None:
        self.assertEqual(
            normalize_url(" HTTPS://Example.COM/test "),
            "https://example.com/test",
        )

    def test_normalize_domain_extracts_domain(self) -> None:
        self.assertEqual(
            normalize_domain("https://WWW.Example.com/test"),
            "www.example.com",
        )

    def test_normalize_email_lowercases_and_strips_punctuation(self) -> None:
        self.assertEqual(
            normalize_email(" INFO@Example.COM, "),
            "info@example.com",
        )

    def test_normalize_telegram_from_handle(self) -> None:
        self.assertEqual(
            normalize_telegram("@Example_Channel"),
            "@example_channel",
        )

    def test_normalize_telegram_from_link(self) -> None:
        self.assertEqual(
            normalize_telegram("https://t.me/Example_Channel/"),
            "@example_channel",
        )

    def test_normalize_telegram_rejects_non_telegram_link(self) -> None:
        self.assertEqual(
            normalize_telegram("https://example.com/contact"),
            "",
        )

    def test_normalize_phone_from_plus7_format(self) -> None:
        self.assertEqual(
            normalize_phone("+7 999 123 45 67"),
            "+79991234567",
        )

    def test_normalize_phone_from_8_format(self) -> None:
        self.assertEqual(
            normalize_phone("8 (999) 123-45-67"),
            "+79991234567",
        )

    def test_normalize_phone_rejects_invalid_number(self) -> None:
        self.assertEqual(
            normalize_phone("12345"),
            "",
        )

    def test_deduplicate_emails(self) -> None:
        self.assertEqual(
            deduplicate_emails([
                "INFO@example.com",
                "info@example.com",
                "sales@example.com",
                "sales@example.com",
            ]),
            ["info@example.com", "sales@example.com"],
        )

    def test_deduplicate_telegrams(self) -> None:
        self.assertEqual(
            deduplicate_telegrams([
                "@Example",
                "https://t.me/example",
                "@another_one",
                "https://telegram.me/another_one",
            ]),
            ["@example", "@another_one"],
        )

    def test_deduplicate_phones(self) -> None:
        self.assertEqual(
            deduplicate_phones([
                "+7 999 123 45 67",
                "8 (999) 123-45-67",
                "+7 912 000 11 22",
            ]),
            ["+79991234567", "+79120001122"],
        )


if __name__ == "__main__":
    unittest.main()