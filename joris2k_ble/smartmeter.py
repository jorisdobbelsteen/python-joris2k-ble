"""
Support for Joris2k Smart Meter
Use update() to retrieve new values, allowing power saving.
Notifications are supported to get updates from device.
"""

import logging
from struct import unpack

from .connection import BTLEConnection

_LOGGER = logging.getLogger(__name__)

PROP_NTFY_HANDLE = 0x421

SMARTMETER_POWER_SVC         = "af880000-558d-47ca-bd46-cb3b6e84b8ac"
SMARTMETER_GAS_SVC           = "4bf70000-e031-4a4f-a0bd-64459a589768"
SMARTMETER_POWER_CONSUMPTION = "af880001-558d-47ca-bd46-cb3b6e84b8ac"
SMARTMETER_POWER_TARIFF      = "af880002-558d-47ca-bd46-cb3b6e84b8ac"
SMARTMETER_POWER_DATE        = 10769
SMARTMETER_POWER_POWER       = "af880003-558d-47ca-bd46-cb3b6e84b8ac"
SMARTMETER_POWER_PHASEINFO   = "af880004-558d-47ca-bd46-cb3b6e84b8ac"
SMARTMETER_GAS_CONSUMPTION   = "4bf70001-e031-4a4f-a0bd-64459a589768"
SMARTMETER_GAS_DATE          = 10769

def _checkedscale(value, divisor):
    if value == -1:
        return None
    return float(value) / divisor

class SmartMeter:
    """Representation of a Joris2k Smart Meter BLE device."""

    def __init__(self, macaddr, connection_cls=BTLEConnection):
        """Initialize the smart meter."""

        # Init variables
        self._clearvalues()

        # Create BLE connection
        self._conn = connection_cls(macaddr)
        # Get BLE characteristics
        #self._cPowerConsumption = self._conn.getCharacteristic(SMARTMETER_POWER_SVC, SMARTMETER_POWER_CONSUMPTION)
        #self._cPowerTariff = self._conn.getCharacteristic(SMARTMETER_POWER_SVC, SMARTMETER_POWER_TARIFF)
        #self._cPowerDate = self._conn.getCharacteristic(SMARTMETER_POWER_SVC, SMARTMETER_POWER_DATE)
        #self._cPowerPower = self._conn.getCharacteristic(SMARTMETER_POWER_SVC, SMARTMETER_POWER_POWER)
        #self._cPowerPhaseInfo = self._conn.getCharacteristic(SMARTMETER_POWER_SVC, SMARTMETER_POWER_PHASEINFO)
        #self._cGasConsumption = self._conn.getCharacteristic(SMARTMETER_GAS_SVC, SMARTMETER_GAS_CONSUMPTION)
        #self._cGasDate = self._conn.getCharacteristic(SMARTMETER_GAS_SVC, SMARTMETER_GAS_DATE)
        # Setup callbacks
        self._conn.set_callback(PROP_NTFY_HANDLE, self.handle_notification)

    def _clearvalues(self):
        self._pwrConsumption = [-1, -1, -1, -1]
        self._pwrTariff = None
        self._pwrPower = [-1, -1, -1]
        self._pwrPower = [-1, -1, -1,  -1, -1, -1,  -1, -1, -1,  -1, -1, -1]
        self._gasConsumption = [-1]

    def handle_notification(self, data):
        """Handle Callback from a Bluetooth (GATT) request."""
        _LOGGER.debug("Received notification from the device..")

    def update(self):
        """Read data from the device."""
        self._clearvalues()  # Ensure all values are reset so we only have the latest data
        _LOGGER.debug("Querying device.")
        self._pwrConsumption = unpack('<iiii', self._conn.readCharacteristic(SMARTMETER_POWER_SVC, SMARTMETER_POWER_CONSUMPTION))
        self._pwrTariff = unpack('<B', self._conn.readCharacteristic(SMARTMETER_POWER_SVC, SMARTMETER_POWER_TARIFF))[0]
        self._pwrPower = unpack('<iii', self._conn.readCharacteristic(SMARTMETER_POWER_SVC, SMARTMETER_POWER_POWER))
        #self._pwrPhaseInfo = unpack('<iiiiiiiiiiii', self._conn.readCharacteristic(SMARTMETER_POWER_SVC, SMARTMETER_POWER_PHASEINFO))
        self._gasConsumption = unpack('<i', self._conn.readCharacteristic(SMARTMETER_GAS_SVC, SMARTMETER_GAS_CONSUMPTION))

    @property
    def power_consumption(self):
        """Total power consumption."""
        if self._pwrConsumption[0] == -1 or self._pwrConsumption[1] == -1:
            return None
        return (self._pwrConsumption[0] + self._pwrConsumption[1]) / 1e3

    @property
    def power_consumption_low(self):
        """Tariff 1 power consumption."""
        return _checkedscale(self._pwrConsumption[0], 1e3)

    @property
    def power_consumption_normal(self):
        """Tariff 2 power consumption."""
        return _checkedscale(self._pwrConsumption[1], 1e3)

    @property
    def power_delivery(self):
        """Total power delivery."""
        if self._pwrConsumption[2] == -1 or self._pwrConsumption[3] == -1:
            return None
        return (self._pwrConsumption[2] + self._pwrConsumption[3]) / 1e3

    @property
    def power_delivery_low(self):
        """Tariff 1 power delivery."""
        return _checkedscale(self._pwrConsumption[2], 1e3)

    @property
    def power_delivery_normal(self):
        """Tariff 2 power delivery."""
        return _checkedscale(self._pwrConsumption[3], 1e3)

    @property
    def current_power_tariff(self):
        """Current active tariff"""
        return self._pwrTariff

    @property
    def current_power_usage(self):
        """Current active power used"""
        if self._pwrPower[0] == -1 and self._pwrPower[1] == -1 and self._pwrPower[2] == -1:
            return None
        return (self._pwrPower[0] + self._pwrPower[1] + self._pwrPower[2]) / 1e3

    # Not implemented yet
    #@property
    #def current_power_usage_per_phase(self):
    #    """Current active tariff"""
    #    return self._pwrTariff

    @property
    def gas_consumption(self):
        """Gas consumption."""
        return _checkedscale(self._gasConsumption[0], 1e3)
