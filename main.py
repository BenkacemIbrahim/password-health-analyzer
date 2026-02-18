"""Main entry point for CLI mode and Tkinter GUI mode."""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Iterable

from gui import PasswordHealthAnalyzerApp
from reuse_detector import detect_reuse
from strength_checker import score_password

log = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Password Health Analyzer CLI")
    parser.add_argument("--password", "-p", help="Password to evaluate")
    parser.add_argument("--test-reuse", action="store_true", help="Run sample reuse detection")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Similarity threshold for reuse checks (0.0 to 1.0).",
    )
    return parser


def _print_reuse_result(passwords: Iterable[str], threshold: float) -> None:
    sample = list(passwords)
    result = detect_reuse(sample, threshold)
    print(f"Sample size: {len(sample)}")
    print("Exact reuses:")
    if result["exact"]:
        for pwd, count in result["exact"].items():
            print(f" - '{pwd}' used {count} times")
    else:
        print(" None")
    print("Similar passwords:")
    if result["similar"]:
        for left, right, similarity in result["similar"]:
            print(f" - '{left}' ~ '{right}' ({similarity:.2f})")
    else:
        print(" None")


def _run_cli(args: argparse.Namespace) -> bool:
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
        _print_reuse_result(sample, args.threshold)
        return True

    if args.password is not None:
        score = score_password(args.password)
        print(f"Strength score: {score}/10")
        return True

    return False


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if _run_cli(args):
        return 0

    log.info("Launching GUI mode")
    app = PasswordHealthAnalyzerApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    sys.exit(main())

