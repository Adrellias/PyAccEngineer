from __future__ import annotations

import struct
from dataclasses import astuple, dataclass
from enum import Enum, auto
from typing import ClassVar, Tuple, List, Union


def rgbtohex(r: int, g: int, b: int) -> str:
    "Convert RGB values to hex"

    return f'#{r:02x}{g:02x}{b:02x}'


def avg(value: Union[List, Tuple]) -> Union[float, int]:

    return sum(value) / len(value)


def string_time_from_ms(time_in_ms: int) -> str:

    # if no time time_in_ms is equal to the maximum value of a 32bit int
    if time_in_ms == 2147483647:
        # simply return 00:00.000
        time_in_ms = 0

    minute = time_in_ms // 60_000
    second = (time_in_ms % 60_000) // 1000
    millisecond = (time_in_ms % 60_000) % 1000

    if minute < 10:
        minute_str = f"0{minute}"

    else:
        minute_str = str(minute)

    if second < 10:
        second_str = f"0{second}"

    else:
        second_str = str(second)

    if millisecond < 100:
        millisecond_str = f"0{millisecond}"

    elif millisecond < 10:
        millisecond_str = f"00{millisecond}"

    else:
        millisecond_str = str(millisecond)

    return f"{minute_str}:{second_str}.{millisecond_str}"


@dataclass
class Credidentials:

    ip: str
    port: int
    username: str
    driverID: int
    driverNb: int


class PacketType(Enum):

    Connect = 1
    SmData = 2
    ServerData = 3
    Disconnect = 4
    ConnectionReply = 5
    Strategy = 6
    StrategyOK = 7
    Telemetry = 8
    UpdateUsers = 9
    Unkown = -1

    def to_bytes(self) -> bytes:
        """
        Convert PacketType to bytes (unsigned char)
        """

        return struct.pack("!B", self.value)

    @classmethod
    def from_bytes(cls, data: bytes) -> PacketType:
        """
        Convert the first unsigned char of a bytes object into a PacketType
        """

        try:
            packet = PacketType(struct.unpack("!B", data[:1])[0])

        except ValueError as msg:

            print(f"PacketType: {msg}")
            packet = PacketType.Unkown

        return packet


class NetworkQueue(Enum):

    ServerData = auto()
    Strategy = auto()
    StrategyDone = auto()
    CarInfoData = auto()
    StrategySet = auto()
    Telemetry = auto()
    UpdateUsers = auto()


@dataclass
class CarInfo:

    front_left_pressure: float
    front_right_pressure: float
    rear_left_pressure: float
    rear_right_pressure: float
    fuel_to_add: float
    max_fuel: float
    tyre_set: int

    byte_format: ClassVar[str] = "!6f i"
    byte_size: ClassVar[int] = struct.calcsize(byte_format)

    def to_bytes(self) -> bytes:

        return struct.pack(self.byte_format, *astuple(self))

    @classmethod
    def from_bytes(cls, data: bytes) -> CarInfo:

        return CarInfo(*struct.unpack(cls.byte_format, data[:cls.byte_size]))


@dataclass
class PitStop:

    fuel: float
    tyre_set: int
    tyre_compound: str
    tyre_pressures: Tuple[float]
    driver_offset: int = 0
    brake_pad: int = 1
    repairs_bodywork: bool = True
    repairs_suspension: bool = True

    byte_format: ClassVar[str] = "!f i 3s 4f 2i 2?"
    byte_size: ClassVar[int] = struct.calcsize(byte_format)

    def to_bytes(self) -> bytes:
        buffer = []
        buffer.append(struct.pack("!f", self.fuel))
        buffer.append(struct.pack("!i", self.tyre_set))
        buffer.append(struct.pack("!3s", self.tyre_compound.encode("utf-8")))
        buffer.append(struct.pack("!4f", *self.tyre_pressures))
        buffer.append(struct.pack("!i", self.driver_offset))
        buffer.append(struct.pack("!i", self.brake_pad))
        buffer.append(struct.pack("!?", self.repairs_bodywork))
        buffer.append(struct.pack("!?", self.repairs_suspension))

        return b"".join(buffer)

    @classmethod
    def from_bytes(cls, data: bytes) -> PitStop:

        temp_data = struct.unpack(cls.byte_format, data[:cls.byte_size])

        pit_data = [
            temp_data[0],
            temp_data[1],
            temp_data[2].decode("utf-8"),
            tuple(temp_data[3:7]),
            temp_data[7],
            temp_data[8],
            temp_data[9],
            temp_data[10],
        ]

        return PitStop(*pit_data)
