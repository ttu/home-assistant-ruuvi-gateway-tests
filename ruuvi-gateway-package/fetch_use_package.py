import asyncio
from ruuvi_gateway import ruuvi_gateway

STATION_IP = "10.0.0.21"
USERNAME = "username"
PASSWORD = "password"


async def main():
    fetch_result = await ruuvi_gateway.fetch_data(STATION_IP, USERNAME, PASSWORD)
    print(
        fetch_result.value if fetch_result.is_ok() else f'Fetch failed: {fetch_result.value}')

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
