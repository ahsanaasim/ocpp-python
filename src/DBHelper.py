
from pymongo import MongoClient
from src.utils.JSONEncoder import JSONEncoder
import json
import certifi


class DBHelper:
    client = None

    def __init__(self):
        self.getDB()

    def getDB(self):
        # tS5BCEmyqHg3Ey27
        # ahsanaasim
        # ocpp-simulator
        # pQ9ila55mMcqrmcL
        CONNECTION_STRING = "mongodb+srv://ocpp-simulator:pQ9ila55mMcqrmcL@6senseocpp.nks6f9q.mongodb.net/?retryWrites=true&w=majority"
        if DBHelper.client is None:
            DBHelper.client = MongoClient(
                CONNECTION_STRING, tlsCAFile=certifi.where())
        return DBHelper.client['ocpp']

    def charger_collection(self, client):
        return client["chargers"]

    def charge_connector_collection(self, client):
        return client["charge_connectors"]
    
    def charge_configuration_collection(self, client):
        return client["charge_configurations"]

    def insert(self, collection, data):
        return collection.insert_one(data)
    
    def insert_many(self, collection, data):
        return collection.insert_many(data)

    def find_one_by_id(self, collection, id):
        return json.loads(JSONEncoder().encode(collection.find_one({"_id": id})))

    def find(self, collection, query):
        return json.loads(JSONEncoder().encode(list(collection.find(query))))

    def find_paginated(self, collection, query, page, limit):
        res = list(collection.find(query).limit(limit).skip((page - 1)*limit))
        return json.loads(JSONEncoder().encode(res))
