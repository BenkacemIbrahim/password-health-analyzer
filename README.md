# Credential Hygiene Analyzer

A local-first Python application for evaluating password strength, detecting password reuse, generating strong credentials, and securely storing password lists.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

## Why this project

Weak and reused passwords remain one of the most common causes of account compromise. This project gives users a private desktop tool to:

- score password strength on a clear 0-10 scale,
- identify exact and near-duplicate passwords,
- generate strong passwords with custom policy constraints,
- save and load encrypted password sets locally.

No cloud sync is used and no telemetry is collected.

## Core features

- Strength analysis (`strength_checker.py`)
- Reuse and similarity detection (`reuse_detector.py`)
- Secure password generation using `secrets` (`generator.py`)
- Encrypted local storage with Fernet when available (`storage.py`)
- Desktop GUI built with Tkinter (`gui.py`)
- CLI entrypoint for quick checks (`main.py`)

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/<your-account>/password-health-analyzer.git
cd password-health-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

GUI mode:

```bash
python main.py
```

CLI strength check:

```bash
python main.py --password "MyS3cure!Passphrase"
```

CLI reuse demo:

```bash
python main.py --test-reuse --threshold 0.85
```

## Keyboard shortcuts (GUI)

| Shortcut | Action |
| --- | --- |
| `Ctrl+A` | Add password |
| `Ctrl+E` | Analyze last password |
| `Ctrl+R` | Check reuse |
| `Ctrl+G` | Generate password |
| `Ctrl+C` | Copy generated password |
| `Ctrl+S` | Save encrypted list |
| `Ctrl+O` | Load encrypted list |
| `Ctrl+L` | Clear list |
| `F2` | Toggle dark mode |

## Security model

- Analysis runs locally on your machine.
- Passwords are never sent to remote services.
- Saved lists are encrypted.
- Preferred storage mode uses `cryptography.fernet`.
- A compatibility fallback exists when `cryptography` is unavailable. For best protection, keep `cryptography` installed.

See `SECURITY.md` for reporting guidance and detailed notes.

## Testing

Run all tests:

```bash
python -m unittest -v
```

Developer tooling:

```bash
pip install -r requirements-dev.txt
```

## Project structure

```text
main.py               # CLI + GUI launcher
gui.py                # Tkinter application
strength_checker.py   # Password scoring logic
reuse_detector.py     # Duplicate/similarity checks
generator.py          # Secure password generation
storage.py            # Encrypted local persistence
tests.py              # Unit test suite
docs/ARCHITECTURE.md  # Design overview
```

## Documentation

- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- `CHANGELOG.md`

## Roadmap

- Add import/export support for CSV and JSON (encrypted at rest).
- Add per-password recommendation explanations in the GUI.
- Add packaged desktop release artifacts.

## License

MIT License. See `LICENSE`.
