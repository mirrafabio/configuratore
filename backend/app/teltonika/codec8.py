"""
Teltonika CODEC 8 and CODEC 8 Extended protocol decoder.

Packet structure:
  [0x00000000]       4 bytes  preamble
  [DataFieldLength]  4 bytes
  [CodecID]          1 byte   0x08 = CODEC8, 0x8E = CODEC8E
  [NumberOfData1]    1 byte
  [AVL Records]      variable
  [NumberOfData2]    1 byte
  [CRC-16/IBM]       4 bytes
"""

import struct
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class GpsElement:
    longitude: float
    latitude: float
    altitude: int
    angle: int
    satellites: int
    speed: int


@dataclass
class IoElement:
    event_io_id: int
    io_data: dict = field(default_factory=dict)


@dataclass
class AvlRecord:
    timestamp: datetime
    priority: int
    gps: GpsElement
    io: IoElement

    @property
    def ignition(self) -> bool:
        return bool(self.io.io_data.get(239, 0))

    @property
    def movement(self) -> bool:
        return bool(self.io.io_data.get(240, 0))

    @property
    def battery_voltage(self) -> Optional[float]:
        raw = self.io.io_data.get(66)
        return raw / 1000.0 if raw is not None else None

    @property
    def gsm_signal(self) -> Optional[int]:
        return self.io.io_data.get(21)

    @property
    def odometer(self) -> Optional[float]:
        raw = self.io.io_data.get(199)
        return raw / 1000.0 if raw is not None else None


def _crc16_ibm(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def decode_packet(data: bytes) -> Optional[list[AvlRecord]]:
    if len(data) < 10:
        return None

    offset = 0
    preamble = struct.unpack_from(">I", data, offset)[0]
    if preamble != 0:
        return None
    offset += 4

    data_length = struct.unpack_from(">I", data, offset)[0]
    offset += 4

    payload = data[offset: offset + data_length]
    if len(payload) < data_length:
        return None

    checksum_bytes = struct.unpack_from(">I", data, offset + data_length)[0]
    calculated = _crc16_ibm(payload)
    if calculated != checksum_bytes:
        return None

    codec_id = payload[0]
    if codec_id not in (0x08, 0x8E):
        return None

    extended = codec_id == 0x8E
    num_records = payload[1]
    pos = 2
    records = []

    for _ in range(num_records):
        ts_ms = struct.unpack_from(">Q", payload, pos)[0]
        pos += 8
        timestamp = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)

        priority = payload[pos]
        pos += 1

        lon_raw = struct.unpack_from(">i", payload, pos)[0]
        pos += 4
        lat_raw = struct.unpack_from(">i", payload, pos)[0]
        pos += 4
        altitude = struct.unpack_from(">H", payload, pos)[0]
        pos += 2
        angle = struct.unpack_from(">H", payload, pos)[0]
        pos += 2
        satellites = payload[pos]
        pos += 1
        speed = struct.unpack_from(">H", payload, pos)[0]
        pos += 2

        gps = GpsElement(
            longitude=lon_raw / 10_000_000.0,
            latitude=lat_raw / 10_000_000.0,
            altitude=altitude,
            angle=angle,
            satellites=satellites,
            speed=speed,
        )

        io_data: dict[int, int] = {}

        if extended:
            event_io_id = struct.unpack_from(">H", payload, pos)[0]
            pos += 2
            total_io = struct.unpack_from(">H", payload, pos)[0]
            pos += 2
        else:
            event_io_id = payload[pos]
            pos += 1
            total_io = payload[pos]
            pos += 1

        for byte_size in (1, 2, 4, 8):
            if extended:
                count = struct.unpack_from(">H", payload, pos)[0]
                pos += 2
            else:
                count = payload[pos]
                pos += 1

            fmt_id = ">H" if extended else "B"
            id_size = 2 if extended else 1

            for _ in range(count):
                if extended:
                    io_id = struct.unpack_from(">H", payload, pos)[0]
                else:
                    io_id = payload[pos]
                pos += id_size

                if byte_size == 1:
                    value = payload[pos]
                elif byte_size == 2:
                    value = struct.unpack_from(">H", payload, pos)[0]
                elif byte_size == 4:
                    value = struct.unpack_from(">I", payload, pos)[0]
                else:
                    value = struct.unpack_from(">Q", payload, pos)[0]
                pos += byte_size
                io_data[io_id] = value

        records.append(AvlRecord(
            timestamp=timestamp,
            priority=priority,
            gps=gps,
            io=IoElement(event_io_id=event_io_id, io_data=io_data),
        ))

    return records
