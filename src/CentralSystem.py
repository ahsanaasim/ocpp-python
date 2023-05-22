import asyncio
from src.ChargePoint import ChargePoint
from ocpp.v16.enums import MessageTrigger, ResetType


class CentralSystem:
    def __init__(self):
        self._chargers = {}

    def register_charger(self, cp: ChargePoint) -> asyncio.Queue:
        """ Register a new ChargePoint at the CSMS. The function returns a
            queue.  The CSMS will put a message on the queue if the CSMS wants to
            close the connection.
            """
        queue = asyncio.Queue(maxsize=1)

        # Store a reference to the task so we can cancel it later if needed.
        task = asyncio.create_task(self.start_charger(
            cp, queue))
        self._chargers[cp] = task
        return queue

    async def start_charger(self, cp, queue):
        try:
            await asyncio.gather(cp.start())
        except Exception as e:
            print(f"Charger {cp.id} disconnected: {e}")
        finally:
            # Make sure to remove reference to charger after it disconnected.
            del self._chargers[cp]
            # This will unblock the `on_connect()` handler and the connection                # will be destroyed.
            await queue.put(True)

    def find_CP(self, id: str) -> ChargePoint:
        for cp, task in self._chargers.items():
            if cp.id == id:
                return cp
        return None

    async def remote_start_transaction(self, id):
        print("CS: remote_start_transaction")
        cp = self.find_CP(id)
        if cp is not None:
            transactionResponse = await cp.remote_start_transaction(cp.id, 1)
            # accepted = "Accepted" : means CP will start
            # rejected = "Rejected" : means CP will not start
            # We need to handle accordingly in the backend
            return transactionResponse
        return None

    async def trigger_message(self, id, message_trigger: str, connector_id=None):
        print("CS: trigger_message")
        # Connector ID is important
        cp = self.find_CP(id)
        if cp is not None:
            triggerResponse = await cp.trigger_message(MessageTrigger[message_trigger], connector_id)
            # accepted = "Accepted": Means CP will trigger the request
            # rejected = "Rejected": Means CP will not trigger the request
            # not_implemented = "NotImplemented": Means CP will not trigger the request
            # We need to handle accordingly in the backend
            return triggerResponse
        return None

    async def change_configuration(self, id, key: str, value: str):
        print("CS: change_configuration")
        cp = self.find_CP(id)
        if cp is not None:
            configResponse = await cp.send_change_configuration_request(key=key, value=value)
            # accepted = "Accepted" : Means config changed
            # rejected = "Rejected": Means can not be changed
            # reboot_required = "RebootRequired" : Means changed but need to reboot** need to find out if it is hard or soft
            # not_supported = "NotSupported" : Means can not be changed
            return configResponse
        return None

    async def reset(self, id, type: str):
        print("CS: reset")
        cp = self.find_CP(id)
        if cp is not None:
            # it cannot be sent if a session is running. handle it from backend. 
            # before sending this need to make the charger offline if online.  handle it from backend. 
            # after the reboot is completed and confirmed through boot notification, charger will be back to online if it was initially online. Otherwise it will stay offline.  handle it from backend. 
            resetResponse = await cp.reset_request(ResetType[type])
            # accepted = "Accepted": Means CP will reset
            # rejected = "Rejected": Means CP will not reset
            return resetResponse
        return None
