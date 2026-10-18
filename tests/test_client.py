"""Offline tests for the API client: no network and no real token are needed."""

import io
import json
import os
import tempfile
import unittest
import urllib.error

from crplanner import ClashRoyaleClient, ClashRoyaleError, load_env_file


class FakeResponse:
    def __init__(self, payload):
        self._body = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class RecordingOpener:
    """Stands in for urllib's urlopen and remembers the request it received."""

    def __init__(self, payload=None, error=None):
        self.payload = payload
        self.error = error
        self.request = None

    def __call__(self, request, timeout=None):
        self.request = request
        if self.error is not None:
            raise self.error
        return FakeResponse(self.payload)


def http_error(code):
    return urllib.error.HTTPError("https://example.test", code, "err", {}, io.BytesIO(b""))


class EncodeTagTests(unittest.TestCase):
    def test_adds_encoded_hash_and_uppercases(self):
        self.assertEqual(ClashRoyaleClient.encode_tag("#abc123"), "%23ABC123")

    def test_accepts_tag_without_hash_and_with_spaces(self):
        self.assertEqual(ClashRoyaleClient.encode_tag("  abc123 "), "%23ABC123")

    def test_empty_tag_is_rejected(self):
        with self.assertRaises(ClashRoyaleError):
            ClashRoyaleClient.encode_tag("  # ")


class ClientTests(unittest.TestCase):
    def test_missing_token_is_rejected(self):
        with self.assertRaises(ClashRoyaleError):
            ClashRoyaleClient("")

    def test_get_cards_builds_url_and_auth_header(self):
        opener = RecordingOpener(payload={"items": [{"name": "Hog Rider"}]})
        client = ClashRoyaleClient("secret-token", opener=opener)

        result = client.get_cards()

        self.assertEqual(result, {"items": [{"name": "Hog Rider"}]})
        self.assertEqual(opener.request.full_url, "https://api.clashroyale.com/v1/cards")
        self.assertEqual(opener.request.get_header("Authorization"), "Bearer secret-token")

    def test_get_player_and_battlelog_encode_the_tag(self):
        opener = RecordingOpener(payload={})
        client = ClashRoyaleClient("t", opener=opener)

        client.get_player("#abc")
        self.assertTrue(opener.request.full_url.endswith("/players/%23ABC"))

        client.get_battlelog("#abc")
        self.assertTrue(opener.request.full_url.endswith("/players/%23ABC/battlelog"))

    def test_http_errors_become_readable_messages(self):
        for code, expected in [(403, "IP"), (404, "tag"), (429, "Demasiadas"), (503, "servidor")]:
            with self.subTest(code=code):
                client = ClashRoyaleClient("t", opener=RecordingOpener(error=http_error(code)))
                with self.assertRaises(ClashRoyaleError) as context:
                    client.get_cards()
                self.assertIn(expected, str(context.exception))

    def test_network_failure_becomes_readable_message(self):
        opener = RecordingOpener(error=urllib.error.URLError("sin red"))
        client = ClashRoyaleClient("t", opener=opener)
        with self.assertRaises(ClashRoyaleError) as context:
            client.get_cards()
        self.assertIn("conexión", str(context.exception))

    def test_token_never_appears_in_error_messages(self):
        client = ClashRoyaleClient("super-secret", opener=RecordingOpener(error=http_error(403)))
        with self.assertRaises(ClashRoyaleError) as context:
            client.get_cards()
        self.assertNotIn("super-secret", str(context.exception))


class LoadEnvFileTests(unittest.TestCase):
    def test_loads_values_without_overriding_existing_ones(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, ".env")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("# comentario\nCR_TEST_A=uno\nCR_TEST_B='dos'\n\nCR_TEST_C=tres\n")

            os.environ.pop("CR_TEST_A", None)
            os.environ.pop("CR_TEST_B", None)
            os.environ["CR_TEST_C"] = "ya-definido"
            try:
                load_env_file(path)
                self.assertEqual(os.environ["CR_TEST_A"], "uno")
                self.assertEqual(os.environ["CR_TEST_B"], "dos")
                self.assertEqual(os.environ["CR_TEST_C"], "ya-definido")
            finally:
                for key in ("CR_TEST_A", "CR_TEST_B", "CR_TEST_C"):
                    os.environ.pop(key, None)

    def test_missing_file_is_ignored(self):
        load_env_file("/ruta/que/no/existe/.env")


if __name__ == "__main__":
    unittest.main()
