# Contributing

## Workflow

1. Create a feature or fix branch from `main` (e.g., `feat/project-stats`, `fix/health-timeout`).
2. Keep changes focused and ensure `core.db_connection` remains the single database access layer.
3. Keep API contracts (`/api/v1/...`) backward-compatible across `home-node` nodes whenever possible.

## Commit Messages and Releases

- Use Conventional Commits where practical: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`.
- Follow Semantic Versioning (`SemVer`) with annotated Git tags (e.g., `v0.1.0`, `v0.2.0`).
