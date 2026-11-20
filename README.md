# home-node-linux

## Database and Connection (Vault)

The service uses centralized secret storage in the `platform_meta` database (`vault` schema, AES-GCM encryption via `core/db_connection`) along with the local `db.py` helper and `psycopg_pool` connection pools. Local `.env` files are not used for database secrets.

* **Database:** `household`
* **Vault Project / User:** `home-node-linux`
* **Mapping in `routes.py` (`PROJECT_VAULT_PROFILES`):** `household` -> `home-node-linux`, `traffic_tracker` -> `home-node-linux`
* **Required Vault Keys:** `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`
* **Legacy Fallback (when project is not found in Vault):** `~/Projects/secure_folder/vpn-dmitry-lab/.env.<project>`

### Why Direct `db.py` Calls Worked While `/api/v1/projects/household/ping` Failed with `fe_sendauth: no password supplied`

* Direct calls to `get_cursor("home-node-linux", "household")` in `db.py` queried the `home-node-linux` Vault profile directly, where all connection parameters (`PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`) were stored.
* Previously, the `/api/v1/projects/{project}/ping` handler in `routes.py` passed the path parameter (`"household"`) directly to `ping_project(project)`. Because `"household"` had no separate Vault entry and `config.py` fell back to an empty password `""`, the connection pool in `db_connection` failed with `fe_sendauth: no password supplied`.
* With `PROJECT_VAULT_PROFILES` configured in `routes.py`, requests to `/api/v1/projects/household/ping` resolve `household` -> `home-node-linux` and pass the `home-node-linux` profile to `ping_project`. Restart the server process after code or connection configuration changes so connection pools are recreated.

### Provisioning Roles, Databases, and Vault Secrets

Use `~/Projects/core/db_connection/provision.sh` (with `.venv` active) to create or update the PostgreSQL role and database and write secrets into Vault:

```bash
cd ~/Projects/home-node-linux
source .venv/bin/activate
PG_HOST=localhost PG_PORT=5432 ~/Projects/core/db_connection/provision.sh