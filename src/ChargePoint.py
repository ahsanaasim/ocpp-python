import logging
import os

from ocpp.v16 import ChargePoint as cp
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result, call
from ocpp.v16.enums import Action, RegistrationStatus, RemoteStartStopStatus, AuthorizationStatus, MessageTrigger, TriggerMessageStatus, ChargePointErrorCode, ChargePointStatus, FirmwareStatus, DiagnosticsStatus, ConfigurationStatus, ResetType, ResetStatus
from datetime import datetime


class ChargePoint(cp):

    async def remote_start_transaction(self, id_tag: str, connector_id: int, charging_profile=None):
        request = call.RemoteStartTransactionPayload(
            id_tag=id_tag,
            connector_id=connector_id,
            charging_profile=charging_profile
        )
        response = await self.call(request)
        return response

    async def trigger_message(self, requested_message: MessageTrigger, connector_id=None):
        request = call.TriggerMessagePayload(
            requested_message=requested_message,
            connector_id=connector_id
        )
        response = await self.call(request)
        return response

    # ----------------------------
    # CP Methods: Means These are called/used from ChargePoint
    # ----------------------------

    # This will be request will be caught by CS in the following
    # Action.BootNotification: on_boot_notification
    async def send_boot_notification(self):

        request = call.BootNotificationPayload(
            charge_point_model="Optimus",
            charge_point_vendor="The Mobility House"
        )

        response = await self.call(request)

        if response.status == RegistrationStatus.accepted:
            print("Connected to central system.", self.id)
            return await self.send_heartbeat()
        return None

    # This will be sent to CS every interval set by CS
    # This request will be caught by CS in the following
    # Action.Heartbeat: on_heartbeat
    async def send_heartbeat(self):
        request = call.HeartbeatPayload()
        response = await self.call(request)
        print(response)
        return response

    # This will be sent to CS
    # This request will be caught by CS in the following
    # Action.StartTransaction: on_start_transaction
    async def send_start_transaction(self, connector_id: int,
                                     id_tag: str,
                                     meter_start: int,
                                     reservation_id: int = None
                                     ):
        request = call.StartTransactionPayload(
            connector_id=connector_id,
            id_tag=id_tag,
            meter_star=meter_start,
            timestamp=datetime.utcnow().isoformat(),
            reservation_id=reservation_id
        )
        response = await self.call(request)
        print(response)
        return response

    # This will be sent to CS
    # This request will be caught by CS in the following
    # Action.StopTransaction: on_stop_transaction
    async def send_stop_transaction(self,
                                    meter_stop: int,
                                    transaction_id: int,
                                    reason: str = None,
                                    id_tag: str = None,
                                    transaction_data: any = None,
                                    ):
        request = call.StopTransactionPayload(
            meter_stop=meter_stop,
            timestamp=datetime.utcnow().isoformat(),
            transaction_id=transaction_id,
            reason=reason,
            id_tag=id_tag,
            transaction_data=transaction_data
        )
        response = await self.call(request)
        print(response)
        return response

    # This will be sent to CS
    # This request will be caught by CS in the following
    # Action.MeterValues: on_meter_values
    async def send_meter_values(self,
                                connector_id: int,
                                meter_value: any,
                                transaction_id: int = None
                                ):
        request = call.MeterValuesPayload(
            connector_id=connector_id,
            meter_value=meter_value,
            transaction_id=transaction_id
        )
        response = await self.call(request)
        print(response)
        return response

    # This will be sent to CS
    # This request will be caught by CS in the following
    # Action.MeterValues: on_meter_values
    async def send_firmware_status_notification(self, status: FirmwareStatus):
        request = call.FirmwareStatusNotificationPayload(status=status)
        response = await self.call(request)
        print(response)
        return response

    # This will be sent to CS
    # This request will be caught by CS in the following
    # Action.FirmwareStatusNotification: on_firmware_status_notification
    async def send_firmware_status_notification(self, status: FirmwareStatus):
        request = call.FirmwareStatusNotificationPayload(status=status)
        response = await self.call(request)
        print(response)
        return response

    # This will be sent to CS
    # This request will be caught by CS in the following
    # Action.DiagnosticsStatusNotification: on_diagnostics_status_notification
    async def send_diagnostics_status_notification(self, status: DiagnosticsStatus):
        request = call.DiagnosticsStatusNotificationPayload(status=status)
        response = await self.call(request)
        print(response)
        return response

    # This will be sent to CS every interval set by CS
    # This request will be caught by CS in the following
    # Action.StatusNotification: on_status_notification
    async def send_status_notification(self,
                                       connector_id: int,
                                       error_code: ChargePointErrorCode,
                                       status: ChargePointStatus,
                                       info: str = None,
                                       vendor_id: str = None,
                                       vendor_error_code: str = None
                                       ):
        # here connector Id is important. If connector id is 0, it means the status of the entire unit, not the plug/connector
        # ********************************
        # The following scenes are possible
        # ********************************
        # available -> preparing, charging, suspendedEV, suspendedEVSE, reserved, unavailable, faulted
        # preparing -> available, charging, suspendedEV, suspendedEVSE, finishing, faulted
        # charging -> available, suspendedEV, suspendedEVSE, finishing, unavailable, faulted
        # suspendedEV -> available, charging, suspendedEVSE, finishing, unavailable, faulted
        # suspendedEVSE -> available, charging, suspendedEV, finishing, unavailable, faulted
        # finishing -> available, preparing, unavailable, faulted
        # we will talk about reserved later
        # unavailable-> available, preparing, charging, suspendedEV, suspendedEVSE, reserved, faulted
        # faulted-> available, preparing, charging, suspendedEV, suspendedEVSE, finishing, reserved, unavailable
        # ********************************
        request = call.StatusNotificationPayload(
            connector_id=connector_id,
            error_code=error_code,
            status=status,
            timestamp=datetime.utcnow().isoformat(),
            info=info,
            vendor_id=vendor_id,
            vendor_error_code=vendor_error_code,
        )
        response = await self.call(request)
        return response

    async def authorize(self, id_tag: str):
        request = call.AuthorizePayload(
            id_tag=id_tag
        )
        response = await self.call(request)
        return response

    @on(Action.RemoteStartTransaction)
    async def on_remote_start_transaction(self, id_tag: str, connector_id: int = None, charging_profile=None):
        # This is CP Method
        # Based on configuration it will return accepted or rejected
        # Check page 49 for the configuration related information
        # some cp may reject if connector id is not passed
        if id_tag == "CUSTOM_CP_C2":
            return call_result.RemoteStartTransactionPayload(status=RemoteStartStopStatus.accepted)
        else:
            return call_result.RemoteStartTransactionPayload(status=RemoteStartStopStatus.rejected)

    @on(Action.TriggerMessage)
    async def on_trigger_message(self, connector_id, requested_message, **kwargs):
        logging.info('CP: TriggerMessage: ' + requested_message)
        # accepted = "Accepted": Means CP will trigger the request
        # rejected = "Rejected": Means CP will not trigger the request
        # not_implemented = "NotImplemented": Means CP will not trigger the request
        return call_result.TriggerMessagePayload(status=TriggerMessageStatus.accepted)

    @on(Action.ChangeConfiguration)
    async def on_change_configuration_request(self, key: str, value: str):
        return call_result.ChangeConfigurationPayload(status=ConfigurationStatus.accepted)
    
    @on(Action.Reset)
    async def on_reset_request(self, type: ResetType):
        return call_result.ResetPayload(status=ResetStatus.accepted)

    # ----------------------------
    # CS Methods: Means These are called/used from CentralSystem
    # ----------------------------

    # This will be sent to CP
    # This request will be caught by CP in the following
    # Action.ChangeConfiguration: on_change_configuration_request
    async def send_change_configuration_request(self, key: str, value: str):
        return call.ChangeConfigurationPayload(key=key, value=value)

    # This will be sent to CP
    # This request will be caught by CP in the following
    # Action.ChangeConfiguration: on_change_configuration_request
    async def reset_request(self, type: ResetType):
        return call.ResetPayload(type=type)

    @on(Action.BootNotification)
    async def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        # This is CS Method
        # Send pending if not found in Redis
        # and do DB Queries. Once DB Operation is done
        # and Redis is updated,
        # Trigger Boot notification again.
        # ----------------------
        # if found in Redis Send Accepted
        # ----------------------
        # if not found in DB send Rejected
        if self.id == "CUSTOM_CP_C1":
            return call_result.BootNotificationPayload(
                current_time=datetime.utcnow().isoformat(),
                interval=10,
                status=RegistrationStatus.pending
            )
        if self.id == "CUSTOM_CP_C2":
            return call_result.BootNotificationPayload(
                current_time=datetime.utcnow().isoformat(),
                interval=10,
                status=RegistrationStatus.accepted
            )
        if self.id == "CUSTOM_CP_C3":
            return call_result.BootNotificationPayload(
                current_time=datetime.utcnow().isoformat(),
                interval=10,
                status=RegistrationStatus.rejected
            )
        else:
            return call_result.BootNotificationPayload(
                current_time=datetime.utcnow().isoformat(),
                interval=10,
                status=RegistrationStatus.accepted
            )

    @on(Action.Heartbeat)
    async def on_heartbeat(self):
        # This is CS Method
        # It should always return HeartBeat. No checks needed here
        return call_result.HeartbeatPayload(current_time=datetime.utcnow().isoformat())

    @on(Action.Authorize)
    async def on_authorization(self, id_tag: str):
        # This is CS Method
        # parentIdTag
        # expiryDate
        # possible statuses accpeted, blocked, expired, invalid, concurrent_tx
        # if Idtag not found invalid
        if id_tag == "CUSTOM_CP_C2":
            return call_result.AuthorizePayload(id_tag_info={
                'status': AuthorizationStatus.accepted
            })
        else:
            return call_result.AuthorizePayload(id_tag_info={
                'status': AuthorizationStatus.accepted
            })

    @on(Action.StatusNotification)
    async def on_status_notification(self, connector_id, error_code, status, **kwargs):
        # here connector Id is important. If connector id is 0, it means the status of the entire unit, not the plug/connector
        logging.info('CS: StatusNotification: ' + status)
        return call_result.StatusNotificationPayload()

    @on(Action.DiagnosticsStatusNotification)
    async def on_diagnostics_status_notification(self, status, **kwargs):
        logging.info('CS: DiagnosticsStatusNotification: ' + status)
        return call_result.DiagnosticsStatusNotificationPayload()

    @on(Action.MeterValues)
    async def on_meter_values(self, connector_id, transaction_id, meter_value, **kwargs):
        logging.info('CS: MeterValues: ' + meter_value)
        # here connector_id is main.
        # connector_id 0 means the entire unit including the energy consumed by the charger itself.
        # connector_id != 0 means the specific plug/connector. Refers to energy consumed in the session.
        # transaction_id is optional.
        # transaction id will not be provided when no session is running
        # transaction id will not be provided when connector_id is 0 or energy is taken from the main meter
        # meter_value is the main. Need to update configuration for full detailed values.
        # returning MeterValuesPayload is a must. Otherwise CP will keep hitting it.
        return call_result.MeterValuesPayload()

    @on(Action.StartTransaction)
    async def on_start_transaction(self, id_tag: str, connector_id: int, meter_start: int, reservationId: int = None, timestamp: str = ''):
        # connector_id needs to match
        # meter_start will be stored
        # reservationId not sure
        # timestamp
        # Transaction Id should be sessionId, our sessionId is string so need to generate another transactionId
        if id_tag == "CUSTOM_CP_C2":
            return call_result.StartTransactionPayload(transaction_id=123, id_tag_info={
                'status': AuthorizationStatus.accepted
            })
        else:
            return call_result.StartTransactionPayload(transaction_id=123, id_tag_info={
                'status': AuthorizationStatus.accepted
            })

    @on(Action.StopTransaction)
    async def on_stop_transaction(self,
                                  meter_stop: int,
                                  transaction_id: int,
                                  timestamp: str,
                                  reason: str = None,
                                  id_tag: str = None,
                                  transaction_data: any = None,
                                  ):
        # id_tag is optional. so it cannot be reliable
        # transaction_id is required. So we should use this
        # Transaction Id should be sessionId, our sessionId is string so need to generate another transactionId
        # returning StopTransactionPayload is a must. Otherwise CP will keep hitting it.
        if id_tag == "CUSTOM_CP_C2":
            return call_result.StopTransactionPayload(id_tag_info={
                'status': AuthorizationStatus.accepted
            })
        else:
            return call_result.StopTransactionPayload(id_tag_info={
                'status': AuthorizationStatus.accepted
            })

    @on(Action.FirmwareStatusNotification)
    async def on_firmware_status_notification(self, status: FirmwareStatus):
        # based on the status, we need to update DB & post socket
        # if status == installed, delete the file from server
        return call_result.FirmwareStatusNotificationPayload()
