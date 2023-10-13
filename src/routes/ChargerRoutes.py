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


class ChargerRoutes:

    @staticmethod
    async def get_all_chargers(request):
        page = int(request.rel_url.query['page'])
        limit = int(request.rel_url.query['limit'])
        res = await Charger().get_chargers(page, limit)
        if res is not None:
            return web.json_response(status=200, data=res)
        return web.json_response(status=404, data=None)
    
    @staticmethod
    async def get_charger_by_id(request):
        charger_id = request.rel_url.query['charger_id']
        res = await Charger().get_by_id(charger_id)
        if res is not None:
            return web.json_response(status=200, data=res)
        return web.json_response(status=404, data=None)

    @ee.on('start_charger_background')
    async def start_charger_background(event, *args, **kwargs):
        res = event
        # cp = ChargePoint(charger_id, ws)
        async with websockets.connect(
            f"{res['data']['central_system_url']}{res['data']['id_tag']}",
            subprotocols=['ocpp1.6']
        ) as ws:
            await Charger().start_charger(res['data']['_id'], True)
            cp = ChargePoint(res['data']['_id'], ws)
            await asyncio.gather(cp.start(), cp.send_boot_notification())
            logging.info("Connected to WebSocket: %s", res['data']['_id'])
        # await asyncio.gather(cp.start(), cp.send_boot_notification())

    @staticmethod
    async def start_charger(request):
        # data = await request.json()
        # charger_id = data['charger_id']
        res = await Charger().get_by_id(request)
        if res is not None:
            # Single().emitter.emit('start_charger_background', res)
            ee.emit('start_charger_background', res)

        return web.json_response(status=200, data=None)

    @staticmethod
    async def add_chargers(request):
        data = await request.json()
        charger = Charger(
            charge_point_model=data['charge_point_model'],
            charge_point_vendor=data['charge_point_vendor'],
            charge_box_serial_number=data['charge_box_serial_number'] if Utils.dict_has_key(
                data, 'charge_box_serial_number') else None,
            charge_point_serial_number=data['charge_point_serial_number'] if Utils.dict_has_key(
                data, 'charge_point_serial_number') else None,
            firmware_version=data['firmware_version'] if Utils.dict_has_key(
                data, 'firmware_version') else None,
            iccid=data['iccid'] if hasattr(data, 'iccid') else None,
            imsi=data['imsi'] if hasattr(data, 'imsi') else None,
            meter_serial_number=data['meter_serial_number'] if Utils.dict_has_key(
                data, 'meter_serial_number') else None,
            meter_type=data['meter_type'] if Utils.dict_has_key(
                data, 'meter_type') else None,
            id_tag=data['id_tag'] if Utils.dict_has_key(
                data, 'id_tag') else None,
            central_system_url=data['central_system_url'] if Utils.dict_has_key(
                data, 'central_system_url') else None,
            charging_rate=data['charging_rate'] if Utils.dict_has_key(
                data, 'charging_rate') else None,
            status=''
        )
        connector_ids = data['connector_ids']
        res = await charger.create()
        res['data']['connectors'] = []
        for connector_id in connector_ids:
            charger_point = ChargerConnector(
                charger_id=res['data']['_id'],
                connector_id=connector_id,
                status='',
            )
            connectorRes = await charger_point.create()
            res['data']['connectors'].append(connectorRes)
        await ChargerConfiguration().create_all_defaults(res['data']['_id'], len(connector_ids))
        return web.json_response(status=res['status'], data=res)
