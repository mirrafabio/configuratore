import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import init_db, AsyncSessionLocal
from app.routers import vehicles, positions, trips, alerts, dashboard
from app.ws_manager import ws_manager

logging.basicConfig(level=logging.INFO)

# Frontend dist: works both locally and on Render
_here = Path(__file__).parent          # backend/app/
STATIC_DIR = (_here / ".." / ".." / "frontend" / "dist").resolve()

TELTONIKA_ENABLED = os.getenv("TELTONIKA_TCP_ENABLED", "true").lower() == "true"


async def _seed_if_empty():
    from sqlalchemy import select, func
    from app.models import Vehicle
    async with AsyncSessionLocal() as db:
        count = (await db.execute(select(func.count()).select_from(Vehicle))).scalar()
        if count == 0:
            demo = [
                {"name": "Furgone Milano 1", "plate": "MI123AB", "model": "Fiat Ducato", "driver": "Marco Rossi", "imei": "352094081234560"},
                {"name": "Furgone Milano 2", "plate": "MI456CD", "model": "Mercedes Sprinter", "driver": "Luca Bianchi", "imei": "352094081234561"},
                {"name": "Auto Commerciale", "plate": "TO789EF", "model": "VW Transporter", "driver": "Sara Verdi", "imei": "352094081234562"},
                {"name": "Camion Roma", "plate": "RM321GH", "model": "Iveco Daily", "driver": None, "imei": "352094081234563"},
                {"name": "Veicolo Frigorifero", "plate": "NA654IJ", "model": "Renault Master", "driver": "Paolo Neri", "imei": "352094081234564"},
            ]
            for v in demo:
                db.add(Vehicle(**v))
            await db.commit()
            logging.getLogger("fleet").info("Seeded %d demo vehicles", len(demo))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await _seed_if_empty()
    if TELTONIKA_ENABLED:
        from app.teltonika.tcp_server import start_tcp_server
        tcp_port = int(os.getenv("TELTONIKA_PORT", "5027"))
        tcp_server = await start_tcp_server(host="0.0.0.0", port=tcp_port)
        async with tcp_server:
            yield
        tcp_server.close()
    else:
        yield


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


# Serve frontend static files when dist directory exists
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")

    @app.get("/vite.svg")
    async def vite_svg():
        return FileResponse(str(STATIC_DIR / "vite.svg"))

    @app.get("/{full_path:path}")
    async def serve_spa(_: str):
        return FileResponse(str(STATIC_DIR / "index.html"))
