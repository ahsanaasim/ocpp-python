from typing import Optional
from datetime import datetime
from dateutil import parser
from bson import ObjectId
from src.models.ChargerConfiguration import ChargerConfiguration
from src.models.ChargerConnector import ChargerConnector
from src.DBHelper import DBHelper
import logging


class Charger:
    def __init__():
        pass

    def __init__(self,
                 charge_point_model: str = "",
                 charge_point_vendor: str = "",
                 id_tag: str = "",
                 central_system_url: str = "",
                 charging_rate: float = 0.0,
                 status: str = "",
                 charge_box_serial_number: Optional[str] = None,
                 charge_point_serial_number: Optional[str] = None,
                 firmware_version: Optional[str] = None,
                 iccid: Optional[str] = None,
                 imsi: Optional[str] = None,
                 meter_serial_number: Optional[str] = None,
                 meter_type: Optional[str] = None):

        self.charge_point_model = charge_point_model
        self.charge_point_vendor = charge_point_vendor
        self.charge_box_serial_number = charge_box_serial_number
        self.charge_point_serial_number = charge_point_serial_number
        self.firmware_version = firmware_version
        self.iccid = iccid
        self.imsi = imsi
        self.meter_serial_number = meter_serial_number
        self.meter_type = meter_type
        self.id_tag = id_tag
        self.central_system_url = central_system_url
        self.charging_rate = charging_rate
        self.status = status

    async def get_chargers(self, page, limit):
        try:
            db = DBHelper()
            if db is not None:
                client = db.getDB()
                if client is not None:
                    charge_collection = db.charger_collection(client=client)
                    res = db.find_paginated(charge_collection, {}, page, limit)
                    if res is None:
                        return None
                    for item in res:
                        id = item['_id']
                        item['connectors'] = await ChargerConnector().get_by_charger_id(ObjectId(id))
                    # res = await db.insert(chargeCollection, data)
                    return {
                        'status': 200,
                        'data': res
                    }
        except Exception as err:
            return {
                'status': 400,
                'message': 'db_error',
                'details': str(err)
            }

        return {
            'status': 400,
            'message': 'unknown_error',
            'details': 'unknown_error'
        }
    
    async def get_by_id(self, id):
        try:
            db = DBHelper()
            if db is not None:
                client = db.getDB()
                if client is not None:
                    charge_collection = db.charger_collection(client=client)
                    res = db.find_one_by_id(charge_collection, ObjectId(id))
                    if res is None:
                        return None
                    res['connectors'] = await ChargerConnector().get_by_charger_id(ObjectId(id))
                    # res = await db.insert(chargeCollection, data)
                    return {
                        'status': 200,
                        'data': res
                    }
        except Exception as err:
            return {
                'status': 400,
                'message': 'db_error',
                'details': str(err)
            }

        return {
            'status': 400,
            'message': 'unknown_error',
            'details': 'unknown_error'
        }

    async def create(self):
        try:
            db = DBHelper()
            if db is not None:
                client = db.getDB()
                if client is not None:
                    date = datetime.utcnow().isoformat()
                    data = {
                        'charge_point_model': self.charge_point_model,
                        'charge_point_vendor': self.charge_point_vendor,
                        'id_tag': self.id_tag,
                        'central_system_url': self.central_system_url,
                        'charging_rate': self.charging_rate,
                        'status': self.status,
                        'charge_box_serial_number': self.charge_box_serial_number,
                        'charge_point_serial_number': self.charge_point_serial_number,
                        'firmware_version': self.firmware_version,
                        'iccid': self.iccid,
                        'imsi': self.imsi,
                        'meter_serial_number': self.meter_serial_number,
                        'meter_type': self.meter_type,
                        'updated_at': parser.parse(date),
                        'created_at': parser.parse(date)
                    }
                    charge_collection = db.charger_collection(client=client)
                    inserted_id = db.insert(
                        charge_collection, data).inserted_id
                    res = db.find_one_by_id(charge_collection, inserted_id)
                    return {
                        'status': 200,
                        'data': res
                    }
        except Exception as err:
            return {
                'status': 400,
                'message': 'db_error',
                'details': str(err)
            }

        return {
            'status': 400,
            'message': 'unknown_error',
            'details': 'unknown_error'
        }

    async def start_charger(self, id, start=True):
        try:
            db = DBHelper()
            if db is not None:
                client = db.getDB()
                if client is not None:
                    date = datetime.utcnow().isoformat()
                    charge_collection = db.charger_collection(client=client)
                    res = charge_collection.update_one({'_id': ObjectId(id)}, {"$set": {
                        "running": start,
                        'updated_at': parser.parse(date),
                    }})
                    return {
                        'status': 200,
                        'data': res
                    }
        except Exception as err:
            return {
                'status': 400,
                'message': 'db_error',
                'details': str(err)
            }

        return {
            'status': 400,
            'message': 'unknown_error',
            'details': 'unknown_error'
        }
