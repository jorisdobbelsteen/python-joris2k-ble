"""
A simple wrapper for bluepy's btle.Connection.
Handles Connection duties (reconnecting etc.) transparently.

Used from https://github.com/rytilahti/python-eq3bt/blob/master/eq3bt/connection.py
"""
import logging
import bleak
import codecs

from bleak import BleakClient
from functools import partial

DEFAULT_TIMEOUT = 1

_LOGGER = logging.getLogger(__name__)


class BTLEConnection:
    """Representation of a BTLE Connection."""

    def __init__(self, mac):
        self._conn = None
        self._mac = mac
        self._callbacks = {}
        self._disconnect_callback = None

        self._conn = BleakClient(mac)
        self._conn.set_disconnected_callback = self.handleDisconnect

    async def connect(self):
        """
        Ensures that device is connected. Otherwise thows exception.
        """
        _LOGGER.debug("Trying to connect to %s", self._mac)
        try:
            await self._conn.connect()
        except bleak.BleakError as ex:
            _LOGGER.debug("Unable to connect to the device %s, retrying: %s", self._mac, ex)
            try:
                await self._conn.connect()
            except Exception as ex2:
                _LOGGER.debug("Second connection try to %s failed: %s", self._mac, ex2)
                raise

        _LOGGER.debug("Connected to %s", self._mac)
        return self

    async def disconnect(self):
        return await self._conn.disconnect()

    def __del__(self):
        # Attempt to disconnect if possible
        #loop = asyncio.get_running_loop()
        #if loop != None:
        #    loop.run_until_complete(self._conn.disconnect())
        self._conn = None

    def handleDisconnect(self, client):
        """Handle Disconnect event from a Bluetooth."""
        _LOGGER.debug("Got BLE disconnect from %s", client.address)
        if self._disconnect_callback != None:
            self._disconnect_callback(client)

    def handleNotification(self, handle, data):
        """Handle Callback from a Bluetooth (GATT) request."""
        _LOGGER.debug("Got BLE notification from %s: %s", handle, codecs.encode(data, 'hex'))
        if handle in self._callbacks:
            self._callbacks[handle](data)

    @property
    def mac(self):
        """Return the MAC address of the connected device."""
        return self._mac

    def set_callback(self, handle, function):
        """Set the callback for a Notification handle. It will be called with the parameter data, which is binary."""
        self._callbacks[handle] = function

    def set_disconnect_callback(self, function):
        """Set the callback upon disconnect."""
        self._disconnect_callback = function

    async def _retry(self, func, max_retry=1):
        for retry in range(0, max_retry):
            try:
                return await func()
            except AttributeError:
                # The `self._bus` object had already been cleaned up due to disconnect...
                _LOGGER.debug("Disconnected, attempting to reconnect to %s before retry", self._mac)
                try:
                    await self.connect()
                except bleak.BleakError:
                    pass
            except bleak.BleakError:
                _LOGGER.debug("BLE error, attempting to reconnect to %s before retry", self._mac)
                try:
                    await self.connect()
                except bleak.BleakError:
                    pass
        if max_retry == 0:
            if not await self._conn.isconnected:
                await self.connect()
        return await func()

    async def _readCharacteristic(self, svc_uuid, characteristic_uuid):
        svcs = await self._conn.get_services()
        svc = svcs.get_service(svc_uuid)
        if svc != None:
            ch = svc.get_characteristic(characteristic_uuid)
            if ch != None:
                return await self._conn.read_gatt_char(ch)
        return None

    async def readCharacteristic(self, svc_uuid, characteristic_uuid):
        return await self._retry(partial(self._readCharacteristic, svc_uuid, characteristic_uuid))
