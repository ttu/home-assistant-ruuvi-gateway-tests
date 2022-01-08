import asyncio
from ruuvi_gateway import ruuvi_gateway

STATION_IP = "10.0.0.21"


async def main():
    data = await ruuvi_gateway.fetch_data(STATION_IP)
    print(data)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())