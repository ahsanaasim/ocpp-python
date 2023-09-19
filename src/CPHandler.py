from ocpp.v16 import ChargePoint as cp
from src.ChargePoint import ChargePoint
import websockets
import asyncio

class CPHandler(cp):
    async def init(id: str):
        async with websockets.connect(
            'ws://localhost:9000/CP_1',
            subprotocols=['ocpp2.0.1']
        ) as ws:
            cp = ChargePoint('CP_1', ws)
