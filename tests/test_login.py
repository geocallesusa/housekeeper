import unittest

import server


class LoginTests(unittest.TestCase):
    def test_valid_credentials(self):
        user = server.validate_login("admin@geovany.com", "housekeeper123")
        self.assertIsNotNone(user)
        self.assertEqual(user["name"], "Geovany Calles")

    def test_invalid_credentials(self):
        self.assertIsNone(server.validate_login("admin@geovany.com", "wrong-password"))


if __name__ == "__main__":
    unittest.main()
