"""Run this script once to populate the database with demo vehicles."""
import asyncio
from app.database import init_db, AsyncSessionLocal
from app.models import Vehicle, VehicleStatus


DEMO_VEHICLES = [
    {"name": "Furgone Milano 1", "plate": "MI123AB", "model": "Fiat Ducato", "driver": "Marco Rossi", "imei": "352094081234560"},
    {"name": "Furgone Milano 2", "plate": "MI456CD", "model": "Mercedes Sprinter", "driver": "Luca Bianchi", "imei": "352094081234561"},
    {"name": "Auto Commerciale", "plate": "TO789EF", "model": "VW Transporter", "driver": "Sara Verdi", "imei": "352094081234562"},
    {"name": "Camion Roma", "plate": "RM321GH", "model": "Iveco Daily", "driver": None, "imei": "352094081234563"},
    {"name": "Veicolo Frigorifero", "plate": "NA654IJ", "model": "Renault Master", "driver": "Paolo Neri", "imei": "352094081234564"},
]


async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        for v in DEMO_VEHICLES:
            vehicle = Vehicle(**v)
            db.add(vehicle)
        await db.commit()
    print(f"Seeded {len(DEMO_VEHICLES)} demo vehicles.")


if __name__ == "__main__":
    asyncio.run(seed())
