# Security Policy

## Supported versions

This project is currently maintained on the latest default branch.

## Reporting a vulnerability

Please do not open public issues for sensitive vulnerabilities.

Use private reporting through repository security advisories when available. Include:

- clear reproduction steps,
- affected files/functions,
- expected security impact,
- suggested mitigation (if known).

Maintainers will acknowledge receipt as soon as practical and work with you on triage, remediation, and coordinated disclosure timing.

## Security notes

- The application is local-first and does not transmit password data remotely.
- Encrypted storage prefers Fernet (`cryptography` package).
- If `cryptography` is unavailable, a compatibility fallback is used. For stronger protection guarantees, keep `cryptography` installed.
- Never commit real credentials or `.pha` files with production data.
