from bson import ObjectId
from datetime import datetime
from dateutil import parser
from src.DBHelper import DBHelper
import logging


class ChargerConnector:
    def __init__(self,
                 charger_id: str="",
                 connector_id: int=0,
                 status: str="",
                 ):

        self.charger_id = charger_id
        self.connector_id = connector_id
        self.status = status

    async def get_by_charger_id(self, charger_id):
        try:
            db = DBHelper()
            if db is not None:
                client = db.getDB()
                if client is not None:
                    charge_collection = db.charge_connector_collection(client=client)
                    res = db.find(charge_collection, {'charger_id': charger_id})
                    return res
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
                        'charger_id': ObjectId(self.charger_id),
                        'connector_id': self.connector_id,
                        'status': self.status,
                        'updated_at': parser.parse(date),
                        'created_at': parser.parse(date)
                    }
                    charge_connector_collection = db.charge_connector_collection(client=client)
                    inserted_id = db.insert(
                        charge_connector_collection, data).inserted_id
                    res = db.find_one_by_id(charge_connector_collection, inserted_id)
                    return res
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
