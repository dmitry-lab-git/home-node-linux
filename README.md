# home-node-linux

Server/WSL node of the **home-node** ecosystem for Linux. Acts as a bridge between network nodes/clients (such as `home-node-android`, and `home-node-ios` in the future) and PostgreSQL databases via the shared `core.db_connection` package.

## Purpose and Role in the Ecosystem

* **`home-node-android`** — local Android node (Ktor + Netty, Room, sync) that accepts external requests and coordinates device-level workflows.
* **`home-node-linux`** — Linux/WSL node that owns the PostgreSQL access layer, reuses connection pools and credentials from `core.db_connection` (`platform_meta` Vault and legacy `.env`), and serves unified responses over shared API contracts.
* **Future Nodes (`home-node-ios`, etc.)** — integrate into the ecosystem using the same protocols and contracts without duplicating database access logic.

## Architectural Principles

1. **Unified DB Access via `core.db_connection`** — no direct database connections bypassing shared connection pools and Vault.
2. **Credential Isolation** — the Vault master key (`~/Projects/secure_folder/vault.yaml`), `platform_meta` access, and database credentials stay strictly on the `home-node-linux` side.
3. **Shared Contracts** — versioned JSON schemas and consistent project/domain identifiers across all nodes.

## Project Structure (Initial Scaffold)

- `README.md`
- `pyproject.toml` (or `requirements.txt`)
- `src/home_node_linux/__init__.py`
- `src/home_node_linux/main.py` — HTTP server entry point
- `src/home_node_linux/config.py` — host, port, timeouts, and allowed projects config
- `src/home_node_linux/routes.py` — `/health`, `/api/v1/...` endpoints
- `src/home_node_linux/bridge.py` — service layer over `core.db_connection`
- `tests/`

## Connecting `core.db_connection`

The `core` package lives alongside this repository (e.g., `~/Projects/core`) and is installed into the `home-node-linux` virtual environment:

    source .venv/bin/activate
    pip install -e ~/Projects/core

## Versioning

This project follows Semantic Versioning (`SemVer`):
* `v0.x.y` — initial development, core architecture, and early API contracts.
* `v1.0.0` — stable inter-node communication contract across the `home-node` ecosystem.
