import uvicorn
from fastapi import FastAPI

from .config import settings
from .routes import router

app = FastAPI(title="home-node-linux", version="0.1.0")
app.include_router(router)


def run() -> None:
    uvicorn.run(
        "home_node_linux.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    run()
