from __future__ import annotations

import atexit
from contextlib import contextmanager
from typing import Iterator
import psycopg
from psycopg_pool import ConnectionPool

from db_connection import vault_loader

_POOLS: dict[tuple[str, str], ConnectionPool] = {}


def _conninfo_for(project: str, db_name: str | None = None) -> str:
    secrets = vault_loader.get_secrets_for_project(project)
    required = ("PGHOST", "PGPORT", "PGDATABASE", "PGUSER", "PGPASSWORD")
    missing = [k for k in required if not secrets.get(k)]
    if missing:
        raise RuntimeError(
            f"В Vault для проекта '{project}' не заданы ключи: {', '.join(missing)}"
        )

    target_db = db_name or secrets["PGDATABASE"]
    return (
        f"host={secrets['PGHOST']} "
        f"port={int(secrets['PGPORT'])} "
        f"dbname={target_db} "
        f"user={secrets['PGUSER']} "
        f"password={secrets['PGPASSWORD']}"
    )


def get_pool(
    project: str = "home-node-linux",
    db_name: str | None = None,
    min_size: int = 1,
    max_size: int = 5,
) -> ConnectionPool:
    secrets = vault_loader.get_secrets_for_project(project)
    target_db = db_name or secrets["PGDATABASE"]
    pool_key = (project, target_db)

    pool = _POOLS.get(pool_key)
    if pool is None:
        conninfo = _conninfo_for(project, db_name=target_db)
        pool = ConnectionPool(
            conninfo=conninfo,
            min_size=min_size,
            max_size=max_size,
            open=True,
        )
        _POOLS[pool_key] = pool
    return pool


@contextmanager
def get_conn(
    project: str = "home-node-linux",
    db_name: str | None = None,
) -> Iterator[psycopg.Connection]:
    pool = get_pool(project=project, db_name=db_name)
    with pool.connection() as conn:
        yield conn


@contextmanager
def get_cursor(
    project: str = "home-node-linux",
    db_name: str | None = None,
) -> Iterator[psycopg.Cursor]:
    with get_conn(project=project, db_name=db_name) as conn:
        try:
            with conn.cursor() as cur:
                yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise


def close_all_pools() -> None:
    for pool in list(_POOLS.values()):
        try:
            pool.close()
        except Exception:
            pass
    _POOLS.clear()


atexit.register(close_all_pools)


if __name__ == "__main__":
    try:
        with get_cursor("home-node-linux", "household") as cur:
            cur.execute("SELECT current_user, current_database(), now()")
            print(cur.fetchone())
    finally:
        close_all_pools()
