from __future__ import annotations

from uvicorn.config import Config
from uvicorn.server import Server

def start_apis():
    config = Config(
        "api.agent_endponts:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )

    server = Server(config)
    server.run()

if __name__ == "__main__":
    start_apis()
