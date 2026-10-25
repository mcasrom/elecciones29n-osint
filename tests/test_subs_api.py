import os
import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from scripts import subs_api


class SubsApiTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_db = subs_api.DB_PATH
        subs_api.DB_PATH = Path(self.tmp.name) / "subs.db"
        subs_api.init_db()

    def tearDown(self):
        subs_api.DB_PATH = self.old_db
        self.tmp.cleanup()

    def test_emails(self):
        self.assertEqual(subs_api.norm_email(" Persona@Example.COM "), "persona@example.com")
        self.assertEqual(subs_api.norm_email("no-es-email"), "")
        self.assertEqual(subs_api.norm_email("a@b"), "")

    def test_referrer(self):
        self.assertEqual(subs_api.ref_host("https://www.google.com/search?q=29n"), "google.com")
        self.assertEqual(subs_api.ref_host("mastodon.social/@x"), "mastodon.social")
        self.assertEqual(subs_api.ref_host(""), "")

    def test_double_opt_in_and_unsubscribe(self):
        token, send = subs_api.subscribe("Persona@Example.com", "29n", "/territorio.html", "mastodon", "social", "29n", "https://mastodon.social/x")
        self.assertTrue(send)
        with subs_api.db() as conn:
            row = conn.execute("SELECT * FROM subscribers WHERE id=?", (token,)).fetchone()
        self.assertEqual(row["consent_version"], subs_api.CONSENT_VERSION)
        self.assertEqual(subs_api.mark_confirmed(token), "ok")
        self.assertEqual(subs_api.mark_confirmed(token), "already")
        self.assertEqual(subs_api.mark_unsubscribed(token), "ok")
        with subs_api.db() as conn:
            row = conn.execute("SELECT * FROM subscribers WHERE id=?", (token,)).fetchone()
        self.assertIsNone(row["page"])
        self.assertIsNone(row["utm_source"])
        self.assertIsNone(row["referrer_host"])
        self.assertEqual(subs_api.mark_unsubscribed(token), "already")
        self.assertEqual(subs_api.mark_confirmed(token), "missing")

    def test_confirmed_does_not_resend(self):
        token, _ = subs_api.subscribe("persona@example.com")
        subs_api.mark_confirmed(token)
        token2, send = subs_api.subscribe("PERSONA@example.com")
        self.assertEqual(token, token2)
        self.assertFalse(send)

    def test_pending_resend_is_throttled(self):
        token, _ = subs_api.subscribe("persona@example.com")
        token2, send = subs_api.subscribe("persona@example.com")
        self.assertEqual(token, token2)
        self.assertFalse(send)

    def test_is_confirmed(self):
        self.assertFalse(subs_api.is_confirmed("persona@example.com"))
        token, _ = subs_api.subscribe("persona@example.com")
        subs_api.mark_confirmed(token)
        self.assertTrue(subs_api.is_confirmed("PERSONA@example.com"))
        self.assertFalse(subs_api.is_confirmed("otra@example.com"))

    def test_rate_limiter(self):
        limiter = subs_api.RateLimiter()
        self.assertTrue(limiter.allow("x", 2, 60))
        self.assertTrue(limiter.allow("x", 2, 60))
        self.assertFalse(limiter.allow("x", 2, 60))

    def test_http_confirm_requires_post(self):
        token, _ = subs_api.subscribe("persona@example.com")
        server = ThreadingHTTPServer(("127.0.0.1", 0), subs_api.Handler)
        server.daemon_threads = True
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            with urllib.request.urlopen(f"{base}/api/confirm?id={token}") as resp:
                html = resp.read().decode("utf-8")
            self.assertIn("Confirma tu suscripción", html)
            self.assertIn('method="post"', html)
            self.assertEqual(subs_api.token_status(token), "pending")
            req = urllib.request.Request(
                f"{base}/api/confirm",
                data=f"id={token}".encode("utf-8"),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urllib.request.urlopen(req) as resp:
                html = resp.read().decode("utf-8")
            self.assertIn("Suscripción confirmada", html)
            self.assertEqual(subs_api.token_status(token), "confirmed")
        finally:
            server.shutdown()
            server.server_close()

    def test_dry_run_send(self):
        old = os.environ.get("RESEND_DRY_RUN")
        os.environ["RESEND_DRY_RUN"] = "1"
        try:
            self.assertTrue(subs_api.send_confirmation("persona@example.com", "token"))
        finally:
            if old is None:
                os.environ.pop("RESEND_DRY_RUN", None)
            else:
                os.environ["RESEND_DRY_RUN"] = old


if __name__ == "__main__":
    unittest.main()
