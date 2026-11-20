import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    host: str = os.getenv("HOME_NODE_HOST", "0.0.0.0")
    port: int = int(os.getenv("HOME_NODE_PORT", "8090"))
    allowed_projects: tuple[str, ...] = tuple(
        p.strip()
        for p in os.getenv("HOME_NODE_ALLOWED_PROJECTS", "household,traffic_tracker").split(",")
        if p.strip()
    )


settings = Settings()
