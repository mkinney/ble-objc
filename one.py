#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Originally from https://github.com/masato-ka/python-corebluetooth-sample.git
# Mike copied from https://raw.githubusercontent.com/simsong/python-corebluetooth/master/scanner.py

# ./one.py --debug
#
# Note: If there is an error, you may need to open up Security and add iTerm to the Bluetooth section.
# TODO: see if we can do a try/catch to print out a nice error message showing the Bluetooth permission (if missing)

import time
import random
import struct
#import logging

import CoreBluetooth
from PyObjCTools import AppHelper
import objc

from constants import C
import datetime

#from google.protobuf.json_format import MessageToJson

import mesh_pb2 as mesh_pb2

MESHTASTIC_SERVICE = CoreBluetooth.CBUUID.UUIDWithString_('0x6BA1B218-15A8-461F-9FA8-5DCAE273EAFD')
TORADIO_UUID = CoreBluetooth.CBUUID.UUIDWithString_("0xF75C76D2-129E-4DAD-A1DD-7866124401E7")
FROMRADIO_UUID = CoreBluetooth.CBUUID.UUIDWithString_("0x8BA2BCC2-EE02-4A55-A531-C525C5E454D5")
FROMNUM_UUID = CoreBluetooth.CBUUID.UUIDWithString_("0xED9DA18C-A800-4F66-A670-AA7547E34453")


random.seed()  # FIXME, we should not clobber the random seedval here, instead tell user they must call it

class MyBLE(CoreBluetooth.NSObject):
    def init(self):
        # ALWAYS call the super's designated initializer.
        # Also, make sure to re-bind "self" just in case it
        # returns something else, or even None!
        self = objc.super(MyBLE, self).init()
        if self is None: return None

        self.manager = None
        self.peripheral = None
        self.service = None

        self.myInfo = None
        self.node = None

        self.debug = False

        self.TORADIO_characteristic = None
        self.FROMRADIO_characteristic = None
        self.FROMNUM_characteristic = None

        # Unlike Python's __init__, initializers MUST return self,
        # because they are allowed to return any object!
        return self

    def centralManager_connectionEventDidOccur_forPeripheral_(self, a, b, c):
        if self.debug:
            print("**centralManager_connectionEventDidOccur_forPeripheral_")
        # TODO?

    def connect(self):
        if self.debug:
            print("connect")
        print('before connect', myBLE.peripheral)
        print('state:', myBLE.peripheral.state())
        print('authorization:', myBLE.manager.authorization())

        if self.manager.isScanning():
            self.manager.stopScan()
            time.sleep(0.1)

        self.manager.connectPeripheral_options_(self.peripheral, None)

        print('peripheral.delegate():', self.peripheral.delegate())
        print('after connect', myBLE.peripheral)

        print('ancsAuthorized:', myBLE.peripheral.ancsAuthorized())

        if self.manager.state() == 5:
            print('manager is in a good state')

    def isScanning(self):
        if self.debug:
            print("**isScanning")

    def peripheralManagerDidUpdateState_(self, foo):
        if self.debug:
            print("**peripheralManagerDidUpdateState_")

    def peripheralManagerIsReadyToUpdateSubscribers_(self, foo):
        if self.debug:
            print("**peripheralManagerIsReadyToUpdateSubscribers_")

    def peripheralManager_central_didSubscribeToCharacteristic_(self, a, b, c):
        if self.debug:
            print("**peripheralManager_central_didSubscribeToCharacteristic_")

    def centralManager_willRestoreState(self):
        if self.debug:
            print("**centralManager_willRestoreState")

    def centralManagerDidUpdateState_(self, manager):
        if self.debug:
            print("**centralManagerDidUpdateState_")
            print(f'manager:{manager}')
        self.manager = manager
        print('manager:', self.manager)
        print('is scanning:', manager.isScanning())
        print('state:', manager.state())
        if manager.state() == 4:
            print('WARNING: Ensure blue tooth is enabled on the computer.')
        if manager.state() == 5:
            print('ready to rock and roll')
        manager.scanForPeripheralsWithServices_options_([MESHTASTIC_SERVICE],None)
        print('is scanning:', manager.isScanning())
        if self.debug:
            print("end of centralManagerDidUpdateState_")

    def discoverCharacteristics_forService_(self, manager, a):
        if self.debug:
            print("**discoverCharacteristics_forService_")

    def centralManager_didDisconnectPeripheral_error_(self, manager, peripheral, error):
        if self.debug:
            print("**centralManager_didDisconnectPeripheral_error_")
            print('manager:', manager)
            print('peripheral:', peripheral)
            print('error:', error)

    def peripheral_didReadRSSI_error(self):
        if self.debug:
            print("**peripheral_didReadRSSI_error")

    def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(self, manager, peripheral, data, rssi):
        if self.debug:
            print('**centralManager_didDiscoverPeripheral_advertisementData_RSSI_')
            print(f'data:{data}')
            print(f'rssi:{rssi}')
            print("\n======== t={} len={}  Channel={} rssi={} =======".format(
                datetime.datetime.now().isoformat(), len(data), data.get(C.kCBAdvDataChannel,'??'), rssi))

        ident = peripheral.identifier()
        name  = peripheral.name()
        try:
            if name is None:
                name = ""
            else:
                name = "Name: " + name
            print("SOURCE: {} {}" .format(ident, name))


            for prop in data.keys():
                if prop==C.kCBAdvDataChannel:
                    continue
                elif prop==C.kCBAdvDataIsConnectable:
                    print("kCBAdvDataIsConnectable: ",data[C.kCBAdvDataIsConnectable])
                elif prop==C.kCBAdvDataManufacturerData:
                    obj = BTLEAdvClassifier( manuf_data = bytes( data[C.kCBAdvDataManufacturerData] ) )
                    print(obj.json(indent=5))
                else:
                    try:
                        for (key,val) in dict(data[prop]).items():
                            print("kCBAdvDataManufacturerData {} = {}".format(key,val))
                    except Exception as e:
                        print(f"data[{prop}] = {data[prop]}")

        except Exception as e:
            print("exception: ",e)

        # stop discovery
        if peripheral and not self.peripheral:
            self.peripheral = peripheral
            self.connect()

    def centralManager_didFailToConnectPeripheral_error_(self, a, b, c):
        if self.debug:
            print("centralManager_didFailToConnectPeripheral_error_")

    def centralManager_didUpdateANCSAuthorizationForPeripheral_(self, a, b):
        if self.debug:
            print("**centralManager_didUpdateANCSAuthorizationForPeripheral_")

    def centralManager_didConnectPeripheral_(self, manager, peripheral):
        if self.debug:
            print("**centralManager_didConnectPeripheral_")
            print(repr(peripheral.UUID()))
        peripheral.setDelegate_(self)
        print('peripheral.delegate():', peripheral.delegate())
        print('self.peripheral.delegate():', self.peripheral.delegate())
        self.peripheral.discoverServices_([MESHTASTIC_SERVICE])

    def peripheral_didDiscoverDescriptorsForCharacteristic_error_(self, a, b, c):
        if self.debug:
            print("**peripheral_didDiscoverDescriptorsForCharacteristic_error_")

    def peripheral_didDiscoverServices_(self, peripheral, services):
        if self.debug:
            print("**peripheral_didDiscoverServices_")
        print('services:', services)
        print('peripheral.services():', peripheral.services())
        print('self.peripheral.services():', self.peripheral.services())
        self.service = self.peripheral.services()[0]
        print('self.service:', self.service)
        self.peripheral.discoverCharacteristics_forService_(None, self.service)

    def peripheral_didDiscoverCharacteristicsForService_error_(self, peripheral, service, error):
        if self.debug:
            print("**peripheral_didDiscoverCharacteristicsForService_error_")
            print('peripheral:', peripheral)
            print('service:', service)
            print('error:', error)
            print('service.characteristics():', service.characteristics())
        self.service = service
        for characteristic in service.characteristics():
            print(f"characteristic.UUID:{characteristic.UUID()}")
            if characteristic.UUID() == TORADIO_UUID:
                self.TORADIO_characteristic = characteristic

                startConfig = mesh_pb2.ToRadio()
                # TODO: use random
                #configId = random.randint(0, 0xffffffff)
                configId = 32168
                startConfig.want_config_id = configId
                print(f'startConfig:{startConfig}')
                binaryData = mesh_pb2.ToRadio.SerializeToString(startConfig)
                print(f'binaryData:{binaryData}')
                peripheral.writeValue_forCharacteristic_type_(binaryData, self.TORADIO_characteristic, CoreBluetooth.CBCharacteristicWriteWithResponse)
                # TODO: getting Encryption is insufficient error

            elif characteristic.UUID() == FROMRADIO_UUID:
                self.FROMRADIO_characteristic = characteristic
                peripheral.readValueForCharacteristic_(self.FROMRADIO_characteristic)

            elif characteristic.UUID() == FROMNUM_UUID:
                self.FROMNUM_characteristic = characteristic
                peripheral.setNotifyValue_forCharacteristic_(True, self.FROMNUM_characteristic)
        print('self.TORADIO_characteristic:', self.TORADIO_characteristic)
        print('self.FROMRADIO_characteristic:', self.FROMRADIO_characteristic)
        print('self.FROMNUM_characteristic:', self.FROMNUM_characteristic)

    def registerForConnectionEventsWithOptions_(self, foo):
        if self.debug:
            print("**registerForConnectionEventsWithOptions_")

    def peripheral_didWriteValueForCharacteristic_error_(self, peripheral, characteristic, error):
        if self.debug:
            print("**peripheral_didWriteValueForCharacteristic_error_")
        print('In error handler')
        print('ERROR:' + repr(error))

    def peripheral_didUpdateNotificationStateForCharacteristic_error_(self, peripheral, characteristic, error):
        if self.debug:
            print("**peripheral_didUpdateNotificationStateForCharacteristic_error_")
            print('peripheral:', peripheral)
            print('characteristic:', characteristic)
            print('error:', error)
        returnValue = None
        if characteristic.UUID() == FROMNUM_UUID:
            peripheral.readValueForCharacteristic_(self.FROMNUM_characteristic)
            characteristicValue = characteristic.value
            print(f'characteristicValue:{characteristicValue}')
            returnValue = characteristicValue
            if returnValue is None:
                return
            # TODO: might have to do some bigEndian and byte order stuff
        elif characteristic.UUID() == FROMRADIO_UUID:
            decodedInfo = mesh_pb2.FromRadio(characteristic.value)
            print(f'decodedInfo:{decodedInfo}')

            # MyInfo Data
            if decodedInfo.myInfo.myNodeNum != 0:
                self.myInfo.myNodeNum = decodedInfo.myInfo.myNodeNum
                self.myInfo.hasGps = decodedInfo.myInfo.hasGps_p
                self.myInfo.numBands = decodedInfo.myInfo.numBands
                # TODO: more fields here

            # NodeInfo Data
            if decodedInfo.nodeInfo.num != 0:
                self.node.id = decodedInfo.nodeInfo.num
                self.node.num = decodedInfo.nodeInfo.num
                # TODO: more fields here

            # Handle assorted app packets
            if decodedInfo.packet.id  != 0:
                # Text Message App - Primary Broadcast User
                if decodedInfo.packet.decoded.portnum == PortNum.textMessageApp:
                    # TODO: utf-8 encoding
                    messageText = decodedInfo.packet.decoded.payload
                # TODO: more types here

# TODO: add sendtext

if "__main__" == __name__:
    import argparse
    parser = argparse.ArgumentParser(description='Read from Meshtastic Radio')
    parser.add_argument("--debug", action='store_true', help="Run with debugger output")
    args = parser.parse_args()

    if args.debug:
        print("after parse_args")

    central_manager = CoreBluetooth.CBCentralManager.alloc()

    if args.debug:
        print("after central_manager")

    myBLE = MyBLE.alloc().init()
    myBLE.debug = args.debug
    central_manager.initWithDelegate_queue_options_(myBLE, None, None)

    if args.debug:
        print("after initWithDelegate")

    try:
        if args.debug:
            print("before runConsoleEventLoop")

        AppHelper.runConsoleEventLoop()

        if args.debug:
            print("after runConsoleEventLoop")

        # TODO: not sure this will ever get called
        print('before cancel', myBLE.peripheral)
        myBLE.manager.cancelPeripheralConnection_(myBLE.peripheral)
        print('aftercancel', myBLE.peripheral)

    except (KeyboardInterrupt, SystemExit) as e:
        print(e)
    except OC_PythonException as e:
        print(e)
        pass
