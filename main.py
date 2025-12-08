"""Main entrypoint providing CLI and launching the Tkinter GUI."""

import argparse
import sys
import logging

from strength_checker import score_password
from reuse_detector import detect_reuse
from gui import PasswordHealthAnalyzerApp


def _run_cli() -> bool:
    parser = argparse.ArgumentParser(description="Password Health Analyzer CLI")
    parser.add_argument("--password", "-p", help="Password to evaluate")
    parser.add_argument("--test-reuse", action="store_true", help="Run sample reuse detection")
    parser.add_argument("--threshold", type=float, default=0.85, help="Similarity threshold for reuse")
    args = parser.parse_args()

    if args.test_reuse:
        sample = [
            "password123",
            "Passw0rd!23",
            "qwerty",
            "qwerty123",
            "A_Stronger-P@ssw0rd!!",
            "A_Str0nger-P@ssw0rd!!",
            "hunter2",
            "hunter3",
            "password123",
        ]
        res = detect_reuse(sample, args.threshold)
        print(f"Sample size: {len(sample)}")
        print("Exact reuses:")
        if res["exact"]:
            for pwd, count in res["exact"].items():
                print(f" - '{pwd}' used {count} times")
        else:
            print(" None")
        print("Similar passwords:")
        if res["similar"]:
            for a, b, s in res["similar"]:
                print(f" - '{a}' ~ '{b}' ({s:.2f})")
        else:
            print(" None")
        return True

    if args.password:
        s = score_password(args.password)
        print(f"Strength score: {s}/10")
        return True

    return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if _run_cli():
        sys.exit(0)
    app = PasswordHealthAnalyzerApp()
    app.mainloop()

