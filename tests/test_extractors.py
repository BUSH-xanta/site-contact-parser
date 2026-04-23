import unittest

from site_contact_parser.extractors import (
    extract_contacts_from_html,
    extract_emails_from_html,
    extract_emails_from_text,
    extract_phones_from_html,
    extract_phones_from_text,
    extract_site_name_from_html,
    extract_telegrams_from_html,
    extract_telegrams_from_text,
)


class TestExtractors(unittest.TestCase):
    def test_extract_site_name_from_html(self) -> None:
        html = """
        <html>
            <head><title>  Example   Site  </title></head>
            <body>Hello</body>
        </html>
        """
        self.assertEqual(extract_site_name_from_html(html), "Example Site")

    def test_extract_emails_from_text(self) -> None:
        text = "Contacts: INFO@example.com, sales@example.com, info@example.com"
        self.assertEqual(
            extract_emails_from_text(text),
            ["info@example.com", "sales@example.com"],
        )

    def test_extract_emails_from_html_includes_mailto_links(self) -> None:
        html = """
        <html>
            <body>
                <p>Email us at info@example.com</p>
                <a href="mailto:sales@example.com">Sales</a>
            </body>
        </html>
        """
        self.assertEqual(
            extract_emails_from_html(html),
            ["info@example.com", "sales@example.com"],
        )

    def test_extract_telegrams_from_text_only_in_telegram_context(self) -> None:
        text = "Telegram: @example_channel"
        self.assertEqual(
            extract_telegrams_from_text(text),
            ["@example_channel"],
        )

    def test_extract_telegrams_from_text_rejects_plain_handle_without_context(self) -> None:
        text = "Contact person: @username"
        self.assertEqual(
            extract_telegrams_from_text(text),
            [],
        )

    def test_extract_telegrams_from_html_from_tme_link(self) -> None:
        html = """
        <html>
            <body>
                <a href="https://t.me/example_channel">Telegram</a>
            </body>
        </html>
        """
        self.assertEqual(
            extract_telegrams_from_html(html),
            ["@example_channel"],
        )

    def test_extract_telegrams_from_html_does_not_treat_regular_links_as_telegram(self) -> None:
        html = """
        <html>
            <body>
                <a href="/about">About</a>
                <a href="/contact">Contact</a>
                <a href="/team">Team</a>
            </body>
        </html>
        """
        self.assertEqual(
            extract_telegrams_from_html(html),
            [],
        )

    def test_extract_phones_from_text(self) -> None:
        text = "Call us: +7 999 123 45 67 or 8 (999) 123-45-67"
        self.assertEqual(
            extract_phones_from_text(text),
            ["+79991234567"],
        )

    def test_extract_phones_from_html_includes_tel_links(self) -> None:
        html = """
        <html>
            <body>
                <p>Phone: +7 912 000 11 22</p>
                <a href="tel:+79991234567">Call now</a>
            </body>
        </html>
        """
        self.assertEqual(
            extract_phones_from_html(html),
            ["+79120001122", "+79991234567"],
        )

    def test_extract_contacts_from_html(self) -> None:
        html = """
        <html>
            <head><title>Example Company</title></head>
            <body>
                <p>Email: info@example.com</p>
                <p>Telegram: @example_channel</p>
                <p>Phone: +7 999 123 45 67</p>
                <a href="mailto:sales@example.com">Sales</a>
                <a href="https://t.me/example_channel">Telegram</a>
                <a href="tel:+79991234567">Call</a>
            </body>
        </html>
        """

        result = extract_contacts_from_html(html)

        self.assertEqual(result["site_name"], "Example Company")
        self.assertEqual(result["emails"], ["info@example.com", "sales@example.com"])
        self.assertEqual(result["telegrams"], ["@example_channel"])
        self.assertEqual(result["phones"], ["+79991234567"])


if __name__ == "__main__":
    unittest.main()