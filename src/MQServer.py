import asyncio
import aio_pika
from pyee import AsyncIOEventEmitter

from src.routes.ChargerRoutes import ChargerRoutes


class MQServer:

    # def __init__(self):
    #     self.init_server()

    async def process_message(
            self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with message.process():
            print(message.body)
            # self.ee.emit('start_charger_background', message.body)
            await ChargerRoutes.start_charger('64723569e4668e768e8863ad')
            await asyncio.sleep(1)

    async def init_server(self):
        connection = await aio_pika.connect_robust(
            "amqp://guest:guest@127.0.0.1/"
        )

        queue_name = "test_queue"

        # Creating channel
        channel = await connection.channel()

        # Maximum message count which will be processing at the same time.
        await channel.set_qos(prefetch_count=100)

        # Declaring queue
        queue = await channel.declare_queue(queue_name, auto_delete=True)

        await queue.consume(self.process_message)

        try:
            # Wait until terminate
            await asyncio.Future()
        finally:
            await connection.close()
