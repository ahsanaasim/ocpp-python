from src.CentralSystem import CentralSystem
from eventemitter import EventEmitter

class Single:
    _self = None

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
            cls.api_url = "http://example.com"
            cls.cs = CentralSystem()
            cls.emitter = EventEmitter()
        return cls._self

    # def __init__(self):
    #     self.api_url = "http://example.com"
    #     self.cs = CentralSystem()

    def track(self):
        print(f"TODO track event at {self.api_url}")