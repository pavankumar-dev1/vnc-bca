import unittest

from app import create_app
from config import TestingConfig


class LogoutRouteTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()

    def _set_authenticated_session(self):
        with self.client.session_transaction() as session:
            session["logged_in"] = True
            session["admin_username"] = "test-admin"
            session["role"] = "admin"

    def test_get_logout_is_not_allowed_and_keeps_session(self):
        self._set_authenticated_session()

        response = self.client.get("/logout")

        self.assertEqual(response.status_code, 405)
        with self.client.session_transaction() as session:
            self.assertTrue(session.get("logged_in"))
            self.assertEqual(session.get("admin_username"), "test-admin")

    def test_post_logout_clears_authenticated_session(self):
        self._set_authenticated_session()

        response = self.client.post("/logout")

        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as session:
            self.assertNotIn("logged_in", session)
            self.assertNotIn("admin_username", session)
            self.assertNotIn("role", session)


if __name__ == "__main__":
    unittest.main()
