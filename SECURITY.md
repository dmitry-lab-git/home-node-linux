# Security Policy

## Credentials and Secrets

- Never commit database passwords, `.env` files, or Vault master keys (`vault.yaml`) to this repository.
- Database connection pooling and credential resolution remain inside `core.db_connection` on the server/WSL host.
- Do not expose raw SQL execution or internal administrative endpoints without authentication and network restrictions.

## Reporting Vulnerabilities

If you find a security issue or accidental secret exposure, report it privately before opening a public issue.
