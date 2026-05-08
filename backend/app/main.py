import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import vehicles, positions, trips, alerts, dashboard
from app.teltonika.tcp_server import start_tcp_server
from app.ws_manager import ws_manager

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    tcp_server = await start_tcp_server(host="0.0.0.0", port=5027)
    async with tcp_server:
        yield
    tcp_server.close()


app = FastAPI(
    title="Fleet Management API",
    description="Piattaforma di gestione flotta con integrazione Teltonika",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vehicles.router, prefix="/api")
app.include_router(positions.router, prefix="/api")
app.include_router(trips.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)


@app.get("/health")
async def health():
    return {"status": "ok"}
