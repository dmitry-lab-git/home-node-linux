from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from db_connection.gateway import ping_project

from .config import settings

router = APIRouter()

# Явное сопоставление имени проекта/БД в API с профилем в Vault
PROJECT_VAULT_PROFILES: dict[str, str] = {
    "household": "home-node-linux",
    "traffic_tracker": "home-node-linux",
}


def _resolve_vault_project(project: str) -> str:
    return PROJECT_VAULT_PROFILES.get(project, project)


def _ok(data: dict[str, Any], status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"ok": True, "data": data, "error": None},
    )


def _err(code: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"ok": False, "data": None, "error": {"code": code, "message": message}},
    )


@router.get("/health")
def health() -> JSONResponse:
    return _ok(
        {
            "status": "ok",
            "node": "home-node-linux",
            "allowed_projects": list(settings.allowed_projects),
        }
    )


@router.get("/api/v1/projects")
def list_projects() -> JSONResponse:
    return _ok({"projects": list(settings.allowed_projects)})


@router.get("/api/v1/projects/{project}/ping")
def project_ping(project: str) -> JSONResponse:
    if project not in settings.allowed_projects:
        return _err(
            code="PROJECT_NOT_ALLOWED",
            message=f"Project '{project}' is not allowed",
            status_code=404,
        )

    vault_project = _resolve_vault_project(project)

    try:
        result = ping_project(vault_project)
        payload = {
            **result,
            "requested_project": project,
            "vault_project": vault_project,
        }
        return _ok(payload)
    except ValueError as exc:
        return _err(
            code="DB_CONFIG_ERROR",
            message=str(exc),
            status_code=500,
        )
    except Exception as exc:
        return _err(
            code="DB_PING_FAILED",
            message=str(exc),
            status_code=500,
        )