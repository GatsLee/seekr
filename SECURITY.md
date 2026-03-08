# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 0.1.x (current) | Yes |

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please use [GitHub Security Advisories](https://github.com/GatsLee/seekr/security/advisories/new) to report vulnerabilities privately.

### What to include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response timeline

- **Acknowledgment:** within 48 hours
- **Initial assessment:** within 7 days
- **Fix release:** within 30 days for critical issues

### Credential security

Seekr handles third-party API credentials (DART, Kakao, Toss, etc.).
If you discover a vulnerability related to credential storage or transmission,
please report it immediately via the process above.

For more details on Seekr's security architecture, see [docs/seekr-security.md](docs/seekr-security.md).
