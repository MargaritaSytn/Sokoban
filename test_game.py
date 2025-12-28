import unittest
from database import hash_password


class TestAuth(unittest.TestCase):
    def test_hash_password(self):
        self.assertEqual(
            hash_password("admin"),
            hash_password("admin")
        )


if __name__ == "__main__":
    unittest.main()
