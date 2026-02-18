# Contributing Guide

Thanks for improving Credential Hygiene Analyzer.

## Development setup

1. Fork and clone the repository.
2. Create a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
pip install -e .[dev]
```

## Running tests

```bash
python -m unittest -v
```

## Coding standards

- Python 3.10+ compatibility.
- Keep user data local and private by default.
- Prefer explicit typing and small, testable functions.
- Keep UI behavior predictable and accessible.

## Pull request checklist

- Add or update tests for behavior changes.
- Update docs when public behavior changes.
- Keep commits focused and reviewable.
- Ensure CI passes before requesting review.

## Commit message style

Use clear, imperative messages, for example:

- `Improve reuse threshold validation`
- `Add storage round-trip tests`
- `Document security model and local-only guarantees`
