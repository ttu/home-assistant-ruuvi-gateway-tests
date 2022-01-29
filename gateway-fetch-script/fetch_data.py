import hashlib
from typing import Generic, Optional, TypeVar, TypedDict
import typing
import asyncio
from aiohttp.client import ClientSession
from attr import dataclass
import aiohttp
from ruuvi_decoders import get_decoder

STATION_IP = "10.0.0.21"
USERNAME = "user"
PASSWORD = "pwd"


class SensorPayload(TypedDict):
    rssi: int
    timestamp: str
    data: str


class PayloadData(TypedDict):
    coordinates: any
    timestamp: str
    gw_mac: str
    tags: typing.Dict[str, SensorPayload]


class Payload(TypedDict):
    data: PayloadData


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


ParsedDatas = typing.Dict[str, SensorData]

T = TypeVar('T')


@dataclass
class Result(Generic[T]):
    data: Optional[T]
    status: Optional[int] = None
    ok: bool = True


def _parse_received_data(payload: Payload) -> ParsedDatas:
    data = payload["data"]
    sensor_datas: ParsedDatas = {}
    for mac, value in data["tags"].items():
        raw = value["data"]

        try:
            companyIndex = raw.index("FF9904")
        except ValueError:
            print("ruuvi company id not found in data")
            continue

        rt: SensorData = {}
        rt["rssi"] = value["rssi"]

        try:
            broadcast_data = raw[companyIndex+6:]
            data_format = broadcast_data[0:2]
            rt = get_decoder(int(data_format)).decode_data(broadcast_data)
        except ValueError:
            print("valid data format data not found in payload")
            continue

        sensor_datas[mac] = rt
    return sensor_datas


def _parse_value_from_header(header: str, key: str):
    ch_start = header.index(key) + len(key) + 2
    ch_end = header.index("\"", ch_start + 1)
    return header[ch_start:ch_end]


def _parse_password(header: str, username: str, password: str):
    challenge = _parse_value_from_header(header, "challenge")
    realm = _parse_value_from_header(header, "realm")
    password_md5 = hashlib.md5(
        f'{username}:{realm}:{password}'.encode()).hexdigest()
    password_sha256 = hashlib.sha256(
        f'{challenge}:{password_md5}'.encode()).hexdigest()
    return password_sha256


def _parse_session_cookie(header: str):
    session_cookie = _parse_value_from_header(header, "session_cookie")
    session_id = _parse_value_from_header(header, "session_id")
    return {session_cookie: session_id}


async def get_auth_info(session: ClientSession, ip, cookies={}):
    async with session.get(f'http://{ip}/auth', cookies=cookies) as response:
        if response.status == 401:
            auth_info = response.headers["WWW-Authenticate"]
            return auth_info
        return None


async def authorize_user(session: ClientSession, ip, cookies, username, password_encrypted):
    auth_payload = '{"login":"' + username + \
        '","password":"' + password_encrypted + '"}'
    async with session.post(f'http://{ip}/auth', data=auth_payload, cookies=cookies) as response:
        return Result(None, response.status, response.status == 200)


async def get_data(session, ip, cookies={}) -> Result[ParsedDatas]:
    try:
        async with session.get(f'http://{ip}/history?time=30', cookies=cookies) as response:
            if response.status == 200:
                data = await response.json()
                parsed = _parse_received_data(data)
                return Result(parsed, 200)
            else:
                return Result(None, response.status, False)
    except aiohttp.ClientConnectionError as e:
        message = e.args[0]
        if hasattr(message, 'code') and message.code == 302:
            return Result(None, 302, False)
        return Result(None, 500, False)


async def get_authenticate_cookies(session, ip, username, password):
    auth_info = await get_auth_info(session, ip)
    cookies = _parse_session_cookie(auth_info)
    password_encrypted = _parse_password(auth_info, username, password)
    auth_result = await authorize_user(session, ip, cookies, username, password_encrypted)
    if not auth_result.ok:
        return Result(None, auth_result.status, False)
    return Result(cookies)


async def fetch_data(ip, username, password) -> Result[Optional[ParsedDatas]]:
    async with aiohttp.ClientSession() as session:
        get_result = await get_data(session, ip)
        if get_result.ok:
            return get_result.data
        if get_result.status != 302:
            print(f'Fetch failed: {get_result.status}')
            return None

        cookie_result = await get_authenticate_cookies(session, ip, username, password)
        if not cookie_result.ok:
            print(f'Auth failed: {cookie_result.status}')
            return None

        get_result = await get_data(session, ip, cookie_result.data)
        if get_result.ok:
            return get_result.data
        else:
            print(f'Fetch failed after authorization: {get_result.status}')


async def main():
    data = await fetch_data(STATION_IP, USERNAME, PASSWORD)
    print(data or "No data")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
