from bson import ObjectId
from datetime import datetime
from dateutil import parser
from src.DBHelper import DBHelper
import logging
from ocpp.v16.enums import ConfigurationKey


class ChargerConfiguration:
    def __init__(self,
                 charger_id: str = "",
                 key: str = "",
                 value: any = "",
                 ):

        self.charger_id = charger_id
        self.key = key
        self.value = value
        self.supported = False
        self.defaults = [{'key': 'AllowOfflineTxForUnknownId', 'supported': True, 'value': '', 'readonly': False},
                         {'key': 'AuthorizationCacheEnabled',
                             'supported': True, 'value': '', 'readonly': False},
                         {'key': 'AuthorizeRemoteTxRequests',
                             'supported': True, 'value': True, 'readonly': True},
                         {'key': 'BlinkRepeat', 'supported': True,
                             'value': '', 'readonly': False},
                         {'key': 'ClockAlignedDataInterval',
                          'supported': True, 'value': 0, 'readonly': False},
                         {'key': 'ConnectionTimeOut', 'supported': True,
                          'value': 300, 'readonly': False},
                         {'key': 'ConnectorPhaseRotation', 'supported': True,
                          'value': 'Unknown', 'readonly': False},
                         {'key': 'ConnectorPhaseRotationMaxLength',
                          'supported': True, 'value': '', 'readonly': False},
                         {'key': 'GetConfigurationMaxKeys',
                          'supported': True, 'value': 1, 'readonly': True},
                         {'key': 'HeartbeatInterval', 'supported': True,
                          'value': 0, 'readonly': False},
                         {'key': 'LightIntensity', 'supported': True,
                          'value': '', 'readonly': False},
                         {'key': 'LocalAuthorizeOffline', 'supported': True,
                          'value': False, 'readonly': False},
                         {'key': 'LocalPreAuthorize', 'supported': True,
                          'value': False, 'readonly': False},
                         {'key': 'MaxEnergyOnInvalidId', 'supported': True,
                          'value': '', 'readonly': False},
                         {'key': 'MeterValuesAlignedData', 'supported': True,
                          'value': 'Energy.Active.Import.Register', 'readonly': False},
                         {'key': 'MeterValuesAlignedDataMaxLength',
                          'supported': True, 'value': '', 'readonly': False},
                         {'key': 'MeterValuesSampledData', 'supported': True,
                          'value': 'Energy.Active.Import.Register', 'readonly': False},
                         {'key': 'MeterValuesSampledDataMaxLength',
                          'supported': True, 'value': '', 'readonly': False},
                         {'key': 'MeterValueSampleInterval', 'supported': True,
                          'value': 300, 'readonly': False},
                         {'key': 'MinimumStatusDuration', 'supported': True,
                          'value': '', 'readonly': False},
                         {'key': 'NumberOfConnectors', 'supported': True,
                          'value': 1, 'readonly': True},
                         {'key': 'ResetRetries', 'supported': True,
                          'value': 0, 'readonly': False},
                         {'key': 'StopTransactionOnEVSideDisconnect',
                          'supported': True, 'value': True, 'readonly': False},
                         {'key': 'StopTransactionOnInvalidId', 'supported': True,
                          'value': True, 'readonly': False},
                         {'key': 'StopTxnAlignedData', 'supported': True,
                          'value': 'Energy.Active.Import.Register', 'readonly': False},
                         {'key': 'StopTxnAlignedDataMaxLength',
                          'supported': True, 'value': '', 'readonly': False},
                         {'key': 'StopTxnSampledData', 'supported': True,
                          'value': 'Energy.Active.Import.Register', 'readonly': False},
                         {'key': 'StopTxnSampledDataMaxLength',
                          'supported': True, 'value': '', 'readonly': False},
                         {'key': 'SupportedFeatureProfiles', 'supported': True,
                          'value': 'Core', 'readonly': True},
                         {'key': 'SupportedFeatureProfilesMaxLength',
                          'supported': True, 'value': '', 'readonly': False},
                         {'key': 'TransactionMessageAttempts',
                          'supported': True, 'value': 0, 'readonly': False},
                         {'key': 'TransactionMessageRetryInterval',
                          'supported': True, 'value': 0, 'readonly': False},
                         {'key': 'UnlockConnectorOnEVSideDisconnect',
                          'supported': True, 'value': True, 'readonly': False},
                         {'key': 'WebSocketPingInterval', 'supported': True,
                          'value': '', 'readonly': False},
                         {'key': 'LocalAuthListEnabled', 'supported': True,
                          'value': '', 'readonly': False},
                         {'key': 'LocalAuthListMaxLength', 'supported': True,
                          'value': '', 'readonly': False},
                         {'key': 'SendLocalListMaxLength', 'supported': True,
                          'value': '', 'readonly': False},
                         {'key': 'ReserveConnectorZeroSupported',
                          'supported': True, 'value': '', 'readonly': False},
                         {'key': 'ChargeProfileMaxStackLevel',
                          'supported': True, 'value': '', 'readonly': False},
                         {'key': 'ChargingScheduleAllowedChargingRateUnit',
                          'supported': True, 'value': '', 'readonly': False},
                         {'key': 'ChargingScheduleMaxPeriods',
                          'supported': True, 'value': '', 'readonly': False},
                         {'key': 'ConnectorSwitch3to1PhaseSupported',
                          'supported': True, 'value': '', 'readonly': False},
                         {'key': 'MaxChargingProfilesInstalled',
                          'supported': True, 'value': '', 'readonly': False},
                         {'key': 'CentralContractValidationAllowed',
                          'supported': True, 'value': '', 'readonly': False},
                         {'key': 'CertificateSignedMaxChainSize',
                          'supported': True, 'value': '', 'readonly': False},
                         {'key': 'CertSigningWaitMinimum', 'supported': True,
                          'value': '', 'readonly': False},
                         {'key': 'CertSigningRepeatTimes', 'supported': True,
                          'value': '', 'readonly': False},
                         {'key': 'CertificateStoreMaxLength',
                          'supported': True, 'value': '', 'readonly': False},
                         {'key': 'ContractValidationOffline',
                          'supported': True, 'value': '', 'readonly': False},
                         {'key': 'ISO15118PnCEnabled', 'supported': True,
                          'value': '', 'readonly': False},
                         {'key': 'AdditionalRootCertificateCheck',
                          'supported': True, 'value': '', 'readonly': False},
                         {'key': 'AuthorizationKey', 'supported': True,
                          'value': '', 'readonly': False},
                         {'key': 'CpoName', 'supported': True,
                             'value': '', 'readonly': False},
                         {'key': 'SecurityProfile', 'supported': True, 'value': '', 'readonly': False}]

    async def get_by_charger_id(self, charger_id, key="ALL"):
        try:
            db = DBHelper()
            if db is not None:
                client = db.getDB()
                if client is not None:
                    charge_configuration_collection = db.charge_configuration_collection(
                        client=client)
                    if key == "ALL":
                        res = db.find(charge_configuration_collection, {
                                      'charger_id': ObjectId(charger_id)})
                        return res
                    else:
                        res = db.find(charge_configuration_collection, {
                                      'charger_id': ObjectId(charger_id), 'key': key})
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

    async def create_all_defaults(self, charger_id, connectors = -1):
        try:
            db = DBHelper()
            if db is not None:
                client = db.getDB()
                if client is not None:
                    date = datetime.utcnow().isoformat()
                    datas = []
                    for item in self.defaults:
                        data = {
                            'charger_id': ObjectId(charger_id),
                            'key': item['key'],
                            'value': item['value'],
                            'supported': item['supported'],
                            'readonly': item['readonly'],
                            'updated_at': parser.parse(date),
                            'created_at': parser.parse(date)
                        }
                        if connectors != 1 and item['key'] == "NumberOfConnectors":
                            data['value'] = connectors

                        datas.append(data)

                    charge_configuration_collection = db.charge_configuration_collection(
                        client=client)
                    inserted_ids = db.insert_many(
                        charge_configuration_collection, datas)
                    
                    return inserted_ids
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
                        'key': self.key,
                        'value': self.value,
                        'supported': self.supported,
                        'updated_at': parser.parse(date),
                        'created_at': parser.parse(date)
                    }
                    charge_configuration_collection = db.charge_configuration_collection(
                        client=client)
                    inserted_id = db.insert(
                        charge_configuration_collection, data).inserted_id
                    res = db.find_one_by_id(
                        charge_configuration_collection, inserted_id)
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
