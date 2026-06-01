import unittest
from scripts.name_resolution import resolve_name

class TestNameResolution(unittest.TestCase):
    def setUp(self):
        self.names = [
            "Alyssa Thomas",
            "Kelsey Mitchell",
            "Breanna Stewart",
            "Jonquel Jones",
            "Nneka Ogwumike",
            "A'ja Wilson",
            "Chelsea Gray",
            "Jewell Loyd",
            "Sabrina Ionescu",
            "Elena Delle Donne"
        ]

    def test_exact_match(self):
        result = resolve_name("Alyssa Thomas", self.names)
        self.assertEqual(result["match"], "Alyssa Thomas")
        self.assertIsNone(result["warning"])

    def test_case_insensitive(self):
        result = resolve_name("alyssa thomas", self.names)
        self.assertEqual(result["match"], "Alyssa Thomas")
        self.assertIsNotNone(result["warning"])

    def test_partial_match(self):
        result = resolve_name("Alyssa", self.names)
        self.assertIsNone(result["match"])
        self.assertIn("Multiple matches", result["warning"])
        self.assertIn("Alyssa Thomas", result["matches"])

    def test_fuzzy_match(self):
        result = resolve_name("Alysa Thomas", self.names)
        self.assertEqual(result["match"], "Alyssa Thomas")
        self.assertIn("Fuzzy match", result["warning"])

    def test_no_match(self):
        result = resolve_name("Nonexistent Player", self.names)
        self.assertIsNone(result["match"])
        self.assertIn("No match found", result["warning"])

    def test_ambiguous(self):
        ambiguous_names = ["Jonquel Jones", "Jon Jones", "Jonah Jones"]
        result = resolve_name("Jon Jones", ambiguous_names)
        self.assertIsNone(result["match"])
        self.assertIn("Multiple matches", result["warning"])
        self.assertIn("Jon Jones", result["matches"])

if __name__ == "__main__":
    unittest.main()
