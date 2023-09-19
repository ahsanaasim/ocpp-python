from aiohttp import web
from Single import Single
from src.models.ChargerConfiguration import ChargerConfiguration
from src.ChargePoint import ChargePoint
from src.models.ChargerConnector import ChargerConnector
from src.models.Charger import Charger
from src.utils.Utils import Utils
import websockets
import asyncio
import logging
from pyee.asyncio import AsyncIOEventEmitter

ee = AsyncIOEventEmitter()


class ChargerConfigurationRoutes:

    @staticmethod
    async def get_charger_configuration_by_charger_id(request):
        charger_id = request.rel_url.query['charger_id']
        key = request.rel_url.query['key'] if Utils.dict_has_key(
            request.rel_url.query, 'key') else None
        
        res = await ChargerConfiguration().get_by_charger_id(charger_id, key if key is not None else "ALL")
        if res is not None:
            return web.json_response(status=200, data=res)
        return web.json_response(status=404, data=None)
