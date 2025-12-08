import unittest
from strength_checker import score_password, analyze_password
from reuse_detector import detect_reuse
from generator import generate_password
from gui import PasswordHealthAnalyzerApp


class TestStrengthChecker(unittest.TestCase):
    def test_empty_password(self):
        self.assertEqual(score_password(""), 0)

    def test_short_password(self):
        self.assertLessEqual(score_password("a"), 2)

    def test_strong_password(self):
        self.assertGreaterEqual(score_password("A_Stronger-P@ssw0rd!!"), 4)

    def test_entropy_and_categories(self):
        res = analyze_password("Abcd1234!@")
        self.assertGreaterEqual(res["entropy_bits"], 30)
        self.assertGreaterEqual(res["categories"], 3)


class TestReuseDetector(unittest.TestCase):
    def test_exact_duplicates(self):
        res = detect_reuse(["password123", "password123", "x"]) 
        self.assertIn("password123", res["exact"]) 
        self.assertEqual(res["exact"]["password123"], 2)

    def test_similarity_detection(self):
        res = detect_reuse(["hunter2", "hunter3"], similarity_threshold=0.8)
        pairs = {(a, b) for a, b, _ in res["similar"]} | {(b, a) for a, b, _ in res["similar"]}
        self.assertTrue(("hunter2", "hunter3") in pairs)

    def test_no_duplicates(self):
        res = detect_reuse(["abc", "def", "ghi"]) 
        self.assertFalse(res["exact"]) 

    def test_budgeted_similarity(self):
        data = [f"item{i}" for i in range(100)]
        res = detect_reuse(data, max_similarity_pairs=10)
        self.assertLessEqual(len(res["similar"]), 10)


class TestGenerator(unittest.TestCase):
    def test_generate_default(self):
        pwd = generate_password()
        self.assertGreaterEqual(len(pwd), 16)
        self.assertGreaterEqual(score_password(pwd), 6)


class TestGUI(unittest.TestCase):
    def test_create_app_and_add(self):
        app = PasswordHealthAnalyzerApp()
        app.passwords.clear()
        app.passwords.append("TestP@ssw0rd!")
        self.assertEqual(len(app.passwords), 1)
        app.destroy()


if __name__ == "__main__":
    unittest.main()
