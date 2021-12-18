joris2k_ble python library
==========================

Supports several BLE smart devices.
Uses bluepy library

Device List
===========

* Smart Meter - sensor for DSMR energy meter on Cypress PSoC4
  https://gitlab.com/jorisdobbelsteen/smartmeter-psoc4

Usage
=====

Setting up bluetooth connection
-------------------------------

The pairing with sensor can be set up using bluetoothctl (which has an interactive prompt):  
  Check the device is not already paired:
  ```
  [bluetooth]# paired-devices  
  ```

  If the device is not present, we proceed with pairing:
  ```
  [bluetooth]# agent off
  [bluetooth]# agent KeyboardOnly
  [bluetooth]# scan on
  ```
  Wait several seconds so devices can be found.
  ```
  [bluetooth]# scan off
  [bluetooth]# devices
  ```
  This should now list the intended target device (between other detected devices).
  ```
  Device 00:A0:50:XX:XX:XX SmartMeter
  ```

  Next up is connecting to the device and entering the passcode (for security):
  ```
  [bluetooth]# connect 00:A0:50:XX:XX:XX
  ```
  This should try to connect to the device and request a passcode with agent prompt. The passcode is provided by sensor firmware on serial debug output.
  ```
  Connection successful
  Request passkey
  [agent] Enter passkey (number in 0-999999): XXXXXX 
  [CHG] Device 00:A0:50:XX:XX:XX Paired: yes
  ```
  Next up, we can set trust, however it's unclear if this is really needed:
  ```
  [SmartMeter]# trust 00:A0:50:XX:XX:XX
  [CHG] Device 00:A0:50:XX:XX:XX Trusted: yes
  Changing 00:A0:50:XX:XX:XX trust succeeded
  ```

  The device should now be listed under paired devices like:
  ```
  [SmartMeter]# paired-devices
  Device 00:A0:50:XX:XX:XX SmartMeter
  [SmartMeter]# info
  Device 00:A0:50:XX:XX:XX (public)
          Name: SmartMeter
          Alias: SmartMeter
          Paired: yes
          Trusted: ???
          Blocked: no
          Connected: yes
          LegacyPairing: no
          UUID: Generic Access Profile    (00001800-0000-1000-8000-00805f9b34fb)
          UUID: Generic Attribute Profile (00001801-0000-1000-8000-00805f9b34fb)
          UUID: Vendor specific           (4bf70000-e031-4a4f-a0bd-64459a589768)
          UUID: Vendor specific           (af880000-558d-47ca-bd46-cb3b6e84b8ac)
  ```

  This is needed to allow other application to connect to the sensor
  ```
  [SmartMeter]# disconnect
  ```

To remove pairing with the device using bluetoothctl:
  ```
  [bluetooth]# disconnect 00:A0:50:XX:XX:XX
  [bluetooth]# remove 00:A0:50:XX:XX:XX
  ```

Alternative method to verify the connection is established correctly is:
```
gatttool -b 00:A0:50:XX:XX:XX --characteristics
  handle = 0x0002, char properties = 0x02, char value handle = 0x0003, uuid = 00002a00-0000-1000-8000-00805f9b34fb
  handle = 0x0004, char properties = 0x02, char value handle = 0x0005, uuid = 00002a01-0000-1000-8000-00805f9b34fb
  handle = 0x0006, char properties = 0x02, char value handle = 0x0007, uuid = 00002a04-0000-1000-8000-00805f9b34fb
  handle = 0x0008, char properties = 0x02, char value handle = 0x0009, uuid = 00002aa6-0000-1000-8000-00805f9b34fb
  handle = 0x000a, char properties = 0x02, char value handle = 0x000b, uuid = 00002ac9-0000-1000-8000-00805f9b34fb
  handle = 0x000d, char properties = 0x20, char value handle = 0x000e, uuid = 00002a05-0000-1000-8000-00805f9b34fb
  handle = 0x0011, char properties = 0x12, char value handle = 0x0012, uuid = af880001-558d-47ca-bd46-cb3b6e84b8ac
  handle = 0x0016, char properties = 0x12, char value handle = 0x0017, uuid = af880002-558d-47ca-bd46-cb3b6e84b8ac
  handle = 0x0019, char properties = 0x12, char value handle = 0x001a, uuid = 00002a11-0000-1000-8000-00805f9b34fb
  handle = 0x001c, char properties = 0x12, char value handle = 0x001d, uuid = af880003-558d-47ca-bd46-cb3b6e84b8ac
  handle = 0x0020, char properties = 0x12, char value handle = 0x0021, uuid = af880004-558d-47ca-bd46-cb3b6e84b8ac
  handle = 0x0025, char properties = 0x12, char value handle = 0x0026, uuid = 4bf70001-e031-4a4f-a0bd-64459a589768
  handle = 0x002a, char properties = 0x12, char value handle = 0x002b, uuid = 00002a11-0000-1000-8000-00805f9b34fb
```

Query device
------------
  Poll current power meter values:
  ```
  ./joris2kblecli.py --mac 00:A0:50:XX:XX:XX info
  ```

  *NOT SUPPORTED YET!* Get BLE events on update (depends on sensor update interval):
  ```
  ./joris2kblecli.py --mac 00:A0:50:XX:XX:XX events
  ```
