import asyncio
import logging
from dotenv import load_dotenv

from src.DBHelper import DBHelper
from src.WebServer import WebServer
from src.CentralSystem import CentralSystem

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

DBHelper()
cs = CentralSystem()


async def main():

    ws = WebServer()
    http_server = await ws.init_http(cs)
    socket_server = await ws.init_socket(cs)

    await asyncio.wait([asyncio.create_task(http_server.start())])
    logging.info("====OREVAI====")
    await asyncio.wait([asyncio.create_task(socket_server.wait_closed())])
    # await asyncio.wait([ws.initChargers("CUSTOM_CP_C1"), ws.initChargers("CUSTOM_CP_C2"), ws.initChargers("CUSTOM_CP_C3"), asyncio.create_task(socket_server.wait_closed())])


if __name__ == '__main__':
    asyncio.run(main())
