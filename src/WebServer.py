from src.CentralSystem import CentralSystem
from src.ChargePoint import ChargePoint

from aiohttp import web
import websockets
import asyncio
import logging


class WebServer:

    # ----------------------------
    # HTTP Server Related Staffs
    # ----------------------------

    async def health(self, request):
        return web.Response(text="<h1> Async Rest API using aiohttp : Health OK </h1>",
                            content_type='text/html')

    async def remote_start_transaction(self, request):
        data = await request.json()
        cs: CentralSystem = request.app["cs"]
        await cs.remote_start_transaction(data["id"])
        return web.Response(text='Request sent successfully: remote_start_transaction')
    
    async def trigger_message(self, request):
        data = await request.json()
        cs: CentralSystem = request.app["cs"]
        await cs.trigger_message(data["id"], data["message_trigger"])
        return web.Response(text='Request sent successfully: trigger_message')
    
    async def reset(self, request):
        data = await request.json()
        cs: CentralSystem = request.app["cs"]
        await cs.reset(data["id"], data["type"])
        return web.Response(text='Request sent successfully: trigger_message')

    async def init_http(self, cs: CentralSystem):
        self.app = web.Application()
        self.app["cs"] = cs
        self.app.add_routes(
            [web.post("/remote-start", self.remote_start_transaction)])
        self.app.add_routes(
            [web.post("/trigger-message", self.trigger_message)])
        self.app.add_routes(
            [web.post("/reset", self.reset)])
        self.app.router.add_get("/", self.health)

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        site = web.TCPSite(self.runner, "0.0.0.0", 6060)
        return site

    async def stop(self):
        await self.runner.cleanup()

    async def initChargers(self, id: str):
        try:
            async with websockets.connect(
                'ws://localhost:9000/' + id,
                subprotocols=['ocpp1.6']
            ) as ws:
                cp = ChargePoint(id, ws)
                logging.info("Connected to WebSocket: %s", id)
                result = await asyncio.gather(cp.start(), cp.send_boot_notification())
                logging.info("Initialization completed for: %s", id)
                return result
        except Exception as e:
            logging.error("Error initializing charger %s: %s", id, str(e))
            return None
        async with websockets.connect(
            'ws://localhost:9000/' + id,
            subprotocols=['ocpp1.6']
        ) as ws:
            cp = ChargePoint(id, ws)
            return await asyncio.gather(cp.start(), cp.send_boot_notification())

    # ----------------------------
    # Socket Server Related Staffs
    # ----------------------------

    async def on_connect(self, websocket, path):
        """ For every new charge point that connects, create a ChargePoint
        instance and start listening for messages.
        """
        try:
            requested_protocols = websocket.request_headers[
                'Sec-WebSocket-Protocol']
        except KeyError:
            logging.info("Client hasn't requested any Subprotocol. "
                         "Closing Connection")
            return await websocket.close()

        if websocket.subprotocol:
            logging.info("Protocols Matched: %s", websocket.subprotocol)
        else:
            # In the websockets lib if no subprotocols are supported by the
            # client and the server, it proceeds without a subprotocol,
            # so we have to manually close the connection.
            logging.warning('Protocols Mismatched | Expected Subprotocols: %s,'
                            ' but client supports  %s | Closing connection',
                            websocket.available_subprotocols,
                            requested_protocols)
            return await websocket.close()

        charge_point_id = path.strip('/')
        cp = ChargePoint(charge_point_id, websocket)
        queue = self.cs.register_charger(cp)
        # await cp.start()
        await queue.get()

    async def init_socket(self, cs: CentralSystem):
        self.cs = cs
        return await websockets.serve(
            self.on_connect,
            '0.0.0.0',
            9000,
            subprotocols=['ocpp1.6']
        )
