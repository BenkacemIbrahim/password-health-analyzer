"""Project test suite."""

from __future__ import annotations

import tempfile
import tkinter as tk
import unittest
from pathlib import Path

try:
    from cryptography.fernet import InvalidToken
except Exception:
    InvalidToken = ValueError

from generator import generate_password
from gui import PasswordHealthAnalyzerApp
from reuse_detector import detect_reuse
from storage import load_passwords, save_passwords
from strength_checker import analyze_password, score_password


class TestStrengthChecker(unittest.TestCase):
    def test_empty_password(self) -> None:
        self.assertEqual(score_password(""), 0)

    def test_short_password(self) -> None:
        self.assertLessEqual(score_password("a"), 2)

    def test_strong_password(self) -> None:
        self.assertGreaterEqual(score_password("A_Stronger-P@ssw0rd!!"), 4)

    def test_entropy_and_categories(self) -> None:
        result = analyze_password("Abcd1234!@")
        self.assertGreaterEqual(result["entropy_bits"], 30)
        self.assertGreaterEqual(result["categories"], 3)


class TestReuseDetector(unittest.TestCase):
    def test_exact_duplicates(self) -> None:
        result = detect_reuse(["password123", "password123", "x"])
        self.assertIn("password123", result["exact"])
        self.assertEqual(result["exact"]["password123"], 2)

    def test_similarity_detection(self) -> None:
        result = detect_reuse(["hunter2", "hunter3"], similarity_threshold=0.8)
        pairs = {(a, b) for a, b, _ in result["similar"]} | {(b, a) for a, b, _ in result["similar"]}
        self.assertIn(("hunter2", "hunter3"), pairs)

    def test_no_duplicates(self) -> None:
        result = detect_reuse(["abc", "def", "ghi"])
        self.assertFalse(result["exact"])

    def test_budgeted_similarity(self) -> None:
        data = [f"item{i}" for i in range(100)]
        result = detect_reuse(data, max_similarity_pairs=10)
        self.assertLessEqual(len(result["similar"]), 10)

    def test_invalid_threshold_raises(self) -> None:
        with self.assertRaises(ValueError):
            detect_reuse(["a", "b"], similarity_threshold=1.2)


class TestGenerator(unittest.TestCase):
    def test_generate_default(self) -> None:
        password = generate_password()
        self.assertGreaterEqual(len(password), 16)
        self.assertGreaterEqual(score_password(password), 6)

    def test_generate_requires_category(self) -> None:
        with self.assertRaises(ValueError):
            generate_password(use_upper=False, use_lower=False, use_digits=False, use_symbols=False)


class TestStorage(unittest.TestCase):
    def test_save_and_load_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "vault.pha"
            data = ["P@ssword1", "Unique#Password2026"]
            save_passwords(path, data, "master-password")
            loaded = load_passwords(path, "master-password")
        self.assertEqual(data, loaded)

    def test_wrong_password_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "vault.pha"
            save_passwords(path, ["value"], "right-password")
            with self.assertRaises((ValueError, InvalidToken)):
                load_passwords(path, "wrong-password")


class TestGUI(unittest.TestCase):
    def test_create_app_and_add(self) -> None:
        try:
            app = PasswordHealthAnalyzerApp()
        except tk.TclError:
            self.skipTest("Tk display is unavailable in this environment.")
            return

        try:
            app.passwords.clear()
            app.passwords.append("TestP@ssw0rd!")
            self.assertEqual(len(app.passwords), 1)
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main(verbosity=2)
