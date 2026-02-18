# Architecture Overview

Credential Hygiene Analyzer is organized as a set of focused modules with a thin CLI/GUI layer.

## Components

- `main.py`
  - Parses CLI flags.
  - Runs one-off command line checks.
  - Launches Tkinter GUI when no CLI action is requested.

- `gui.py`
  - Provides desktop workflows for adding, analyzing, generating, saving, and loading passwords.
  - Uses a shared style system with light/dark palettes.

- `strength_checker.py`
  - Computes strength score and supporting metrics:
    - character categories,
    - estimated entropy,
    - common-password check,
    - monotonic/keyboard sequence detection,
    - repeated-character pattern detection.

- `reuse_detector.py`
  - Detects exact duplicates in O(n).
  - Detects near-duplicates with bounded pairwise comparison (`max_similarity_pairs`).

- `generator.py`
  - Builds passwords from enabled character categories.
  - Guarantees at least one character from each enabled category.
  - Uses `secrets` for cryptographically strong randomness.

- `storage.py`
  - Serializes password lists to encrypted `.pha` files.
  - Preferred path: Fernet encryption (`cryptography`).
  - Compatibility fallback: PBKDF2 + HMAC-checked XOR stream.

## Data flow

1. User inputs a password (GUI/CLI).
2. Strength score is computed via `strength_checker`.
3. Reuse checks call `reuse_detector`.
4. Generated passwords come from `generator`.
5. Save/load routes through `storage` with password-derived keys.

## Design principles

- Local-first privacy.
- Small modules with clear responsibilities.
- Secure defaults where library support exists.
- Deterministic, testable behavior.
