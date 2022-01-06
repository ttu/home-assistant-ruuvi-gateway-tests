import asyncio
import aiohttp
from ruuvi_decoders import get_decoder

STATION_IP = "10.0.0.21"


def parse(data):
    data = data["data"]
    sensor_datas = {}
    for mac in data["tags"]:
        raw = data["tags"][mac]["data"]

        try:
            companyIndex = raw.index("FF9904")
        except ValueError:
            print("ruuvi company id not found in data")
            continue

        rt = {}
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


async def fetchData(ip, pollRate):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://'+ip+'/history?time='+str(pollRate), allow_redirects=False) as response:
            if response.status == 200:
                data = await response.json()
                return parse(data)
            else:
                print("Response status:", response.status)


async def main():
    data = await fetchData(STATION_IP, 30)
    print(data)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
