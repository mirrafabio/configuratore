"""
Async TCP server that handles Teltonika device connections.

Protocol handshake:
  1. Device connects and sends IMEI packet: [2-byte length][IMEI string]
  2. Server replies 0x01 (accepted) or 0x00 (rejected)
  3. Device sends AVL data packets
  4. Server replies with [4-byte big-endian number of records received]
"""

import asyncio
import json
import logging
import struct
from datetime import datetime, timezone

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Vehicle, Position, Trip, Alert, VehicleStatus, AlertType
from app.teltonika.codec8 import decode_packet, AvlRecord
from app.ws_manager import ws_manager

logger = logging.getLogger("teltonika.tcp")

SPEED_ALERT_THRESHOLD = 130  # km/h


async def _get_or_reject_vehicle(imei: str) -> int | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Vehicle).where(Vehicle.imei == imei))
        vehicle = result.scalar_one_or_none()
        if vehicle is None:
            logger.warning("Unknown IMEI %s – connection rejected", imei)
            return None
        return vehicle.id


async def _process_records(vehicle_id: int, records: list[AvlRecord]):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
        vehicle = result.scalar_one()

        prev_ignition = vehicle.status != VehicleStatus.offline

        for rec in records:
            if rec.gps.satellites < 3:
                continue

            position = Position(
                vehicle_id=vehicle_id,
                timestamp=rec.timestamp,
                latitude=rec.gps.latitude,
                longitude=rec.gps.longitude,
                altitude=rec.gps.altitude,
                angle=rec.gps.angle,
                speed=rec.gps.speed,
                satellites=rec.gps.satellites,
                ignition=rec.ignition,
                movement=rec.movement,
                battery_voltage=rec.battery_voltage,
                gsm_signal=rec.gsm_signal,
                odometer=rec.odometer,
                raw_io=json.dumps(rec.io.io_data),
            )
            db.add(position)

            if rec.gps.speed > 0:
                vehicle.status = VehicleStatus.moving
            elif rec.ignition:
                vehicle.status = VehicleStatus.idle
            else:
                vehicle.status = VehicleStatus.offline

            vehicle.last_seen = datetime.now(tz=timezone.utc)

            if rec.gps.speed > SPEED_ALERT_THRESHOLD:
                alert = Alert(
                    vehicle_id=vehicle_id,
                    type=AlertType.speeding,
                    message=f"Velocità {rec.gps.speed} km/h rilevata",
                    latitude=rec.gps.latitude,
                    longitude=rec.gps.longitude,
                    speed=rec.gps.speed,
                )
                db.add(alert)

            if rec.ignition and not prev_ignition:
                db.add(Alert(
                    vehicle_id=vehicle_id,
                    type=AlertType.ignition_on,
                    message="Accensione rilevata",
                    latitude=rec.gps.latitude,
                    longitude=rec.gps.longitude,
                ))
                db.add(Trip(
                    vehicle_id=vehicle_id,
                    start_time=rec.timestamp,
                    start_lat=rec.gps.latitude,
                    start_lng=rec.gps.longitude,
                ))

            elif not rec.ignition and prev_ignition:
                db.add(Alert(
                    vehicle_id=vehicle_id,
                    type=AlertType.ignition_off,
                    message="Spegnimento rilevato",
                    latitude=rec.gps.latitude,
                    longitude=rec.gps.longitude,
                ))

            prev_ignition = rec.ignition

        await db.commit()

    await ws_manager.broadcast({
        "type": "position_update",
        "vehicle_id": vehicle_id,
    })


async def _handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    logger.info("New connection from %s", addr)

    try:
        # Read IMEI packet
        imei_len_bytes = await asyncio.wait_for(reader.readexactly(2), timeout=10)
        imei_len = struct.unpack(">H", imei_len_bytes)[0]
        imei_bytes = await asyncio.wait_for(reader.readexactly(imei_len), timeout=10)
        imei = imei_bytes.decode("ascii").strip()
        logger.info("IMEI received: %s from %s", imei, addr)

        vehicle_id = await _get_or_reject_vehicle(imei)
        if vehicle_id is None:
            writer.write(b"\x00")
            await writer.drain()
            return

        writer.write(b"\x01")
        await writer.drain()
        logger.info("IMEI %s accepted (vehicle_id=%d)", imei, vehicle_id)

        # Main data loop
        while True:
            # Read preamble + data length (8 bytes)
            header = await asyncio.wait_for(reader.readexactly(8), timeout=60)
            data_len = struct.unpack_from(">I", header, 4)[0]

            # codec(1) + records(1) + avl + records(1) + crc(4) = data_len + 5
            rest = await asyncio.wait_for(
                reader.readexactly(data_len + 4), timeout=30
            )
            packet = header + rest

            records = decode_packet(packet)
            if records is None:
                logger.warning("Invalid packet from IMEI %s", imei)
                continue

            logger.info("Received %d records from IMEI %s", len(records), imei)
            await _process_records(vehicle_id, records)

            ack = struct.pack(">I", len(records))
            writer.write(ack)
            await writer.drain()

    except asyncio.IncompleteReadError:
        logger.info("Device %s disconnected", addr)
    except asyncio.TimeoutError:
        logger.warning("Timeout on connection %s", addr)
    except Exception as exc:
        logger.error("Error handling %s: %s", addr, exc, exc_info=True)
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass


async def start_tcp_server(host: str = "0.0.0.0", port: int = 5027):
    server = await asyncio.start_server(_handle_client, host, port)
    logger.info("Teltonika TCP server listening on %s:%d", host, port)
    return server
