from typing import Optional, TypedDict
import asyncio
import typing
import aiohttp
from attr import dataclass
from ruuvi_decoders import get_decoder

STATION_IP = "10.0.0.21"
POLL_RATE = 30


class SensorData(TypedDict):
    data_format: int
    humidity: float
    temperature: float
    pressure: float
    acceleration: float
    acceleration_x: float
    acceleration_y: float
    acceleration_z: float
    battery: int
    tx_power: Optional[int]
    movement_counter:  Optional[int]
    measurement_sequence_number:  Optional[int]
    mac: Optional[str]
    rssi: Optional[int]


@dataclass
class Result:
    code: int
    payload: any


def _parse(data: dict) -> typing.Dict[str, SensorData]:
    data = data["data"]
    sensor_datas: typing.Dict[str, SensorData] = {}
    for mac in data["tags"]:
        raw = data["tags"][mac]["data"]

        try:
            companyIndex = raw.index("FF9904")
        except ValueError:
            print("ruuvi company id not found in data")
            continue

        rt: SensorData = {}
        rt["rssi"] = data["tags"][mac]["rssi"]

        try:
            broadcast_data = raw[companyIndex+6:]
            data_format = broadcast_data[0:2]
            rt = get_decoder(int(data_format)).decode_data(broadcast_data)
        except ValueError:
            print("valid data format data not found in payload")
            continue

        sensor_datas[mac] = rt
    return sensor_datas


async def get_auth_info(session, ip):
    async with session.get('http://'+ip+'/auth', allow_redirects=False) as response:
        if response.status == 401:
            auth_info = response.headers["WWW-Authenticate"]
            return auth_info
        return None


async def get_data(session, ip) -> Result:
    try:
        async with session.get('http://'+ip+'/history?time='+str(POLL_RATE), allow_redirects=False) as response:
            if response.status == 200:
                data = await response.json()
                parsed = _parse(data)
                return Result(200, parsed)
            else:
                return Result(response.status, None)
    except aiohttp.ClientConnectionError as e:
        message = e.args[0]
        if message is not None and message.code == 302:
            return Result(302, None)
        return Result(500, None)


def parse_value(header: str, key: str):
    ch_start = header.index(key) + len(key) + 2
    ch_end = header.index("\"", ch_start + 1)
    return header[ch_start:ch_end]

async def fetch_data(ip):
    async with aiohttp.ClientSession() as session:
        result = await get_data(session, ip)
        print("Response status:", result.code)

        if result.code == 200:
            return result.payload
        if (result.code == 302):
            auth_info = await get_auth_info(session, ip)
            challenge = parse_value(auth_info, "challenge")
            realm = parse_value(auth_info, "realm")
            print(challenge)
            print(realm)
            print(auth_info)


async def main():
    data = await fetch_data(STATION_IP)
    print(data)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
