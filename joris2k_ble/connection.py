"""
A simple wrapper for bluepy's btle.Connection.
Handles Connection duties (reconnecting etc.) transparently.

Used from https://github.com/rytilahti/python-eq3bt/blob/master/eq3bt/connection.py
"""
import logging
import codecs

from bluepy import btle
from functools import partial

DEFAULT_TIMEOUT = 1

_LOGGER = logging.getLogger(__name__)


class BTLEConnection(btle.DefaultDelegate):
    """Representation of a BTLE Connection."""

    def __init__(self, mac):
        """Initialize the connection."""
        btle.DefaultDelegate.__init__(self)

        self._conn = None
        self._mac = mac
        self._callbacks = {}

        self._conn = btle.Peripheral()
        self._conn.withDelegate(self)

        try:
            self._connect()
        except btle.BTLEDisconnectError:
            pass

    def _connect(self):
        """
        Ensures that device is connected. Otherwise thows exception.
        """
        _LOGGER.debug("Trying to connect to %s", self._mac)
        try:
            self._conn.connect(self._mac)
        except btle.BTLEException as ex:
            _LOGGER.debug("Unable to connect to the device %s, retrying: %s", self._mac, ex)
            try:
                self._conn.connect(self._mac)
            except Exception as ex2:
                _LOGGER.debug("Second connection try to %s failed: %s", self._mac, ex2)
                raise

        _LOGGER.debug("Connected to %s", self._mac)
        return self

    def __del__(self):
        self._conn.disconnect()
        self._conn = None

    def handleNotification(self, handle, data):
        """Handle Callback from a Bluetooth (GATT) request."""
        _LOGGER.debug("Got notification from %s: %s", handle, codecs.encode(data, 'hex'))
        if handle in self._callbacks:
            self._callbacks[handle](data)

    @property
    def mac(self):
        """Return the MAC address of the connected device."""
        return self._mac

    def set_callback(self, handle, function):
        """Set the callback for a Notification handle. It will be called with the parameter data, which is binary."""
        self._callbacks[handle] = function

    def _retry(self, func, max_retry=1):
        for retry in range(1, max_retry):
            try:
                return func()
            except btle.BTLEException:
                try:
                    self._connect()
                except btle.BTLEDisconnectError:
                    pass
        return func()

    def _readCharacteristic(self, svc_uuid, characteristic_uuid):
        svc = self._conn.getServiceByUUID(btle.UUID(svc_uuid))
        char = svc.getCharacteristics(btle.UUID(characteristic_uuid))[0]
        return char.read()

    def readCharacteristic(self, svc_uuid, characteristic_uuid):
        return self._retry(partial(self._readCharacteristic, svc_uuid, characteristic_uuid))
