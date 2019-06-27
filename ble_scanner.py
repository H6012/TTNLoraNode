#!/usr/bin/env python
#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

from network import LoRa
import socket
import time
import utime
import ubinascii
import pycom
import machine
import ujson

from network import Bluetooth
import machine
import binascii
import gc

from ring import RingBuffer






class BLEScanner:

    def __init__(self, buffer_size):
        """Store buffer in given storage."""
        self.beaconlist = []
        self.beacontime = []
        self.beaconrssi = []
        self.beaconevents = []
        self.beaconcount=[]
        self.timelastdata = time.time()
        self.eventBuffer=RingBuffer(buffer_size)
        self.bluetooth = Bluetooth()

    def new_adv_event(self, event):
        global beaconlist, beaconevents, timelastdata
        if event.events() == Bluetooth.NEW_ADV_EVENT:
            anydata = True
            while anydata:
                adv = self.bluetooth.get_adv()
                if adv != None:
                    timelastdata = time.time()
                    devid = binascii.hexlify(adv[0]).decode('utf-8')
                    rssi = str(adv[3]*-1)
                    if devid not in self.beaconlist:
                        print('new device found {} @ {}'.format(devid,timelastdata))
                        self.beaconlist.append(devid)
                        self.beacontime.append(timelastdata)
                        self.beaconrssi.append(rssi)
                        self.beaconcount.append(0)
                        #if len(beaconevents) > 20:
                        #    beaconevents.pop(0)
                        #beaconevents.append([timelastdata, devid, rssi])
                        self.eventBuffer.add([timelastdata, devid, rssi, 0])

                    else:
                        #find index in array of this beacon and check the timelastdata
                        #update beaconrssi
                        #decide if stuff shoudl be pushed again
                        i = self.beaconlist.index(devid)

                        if self.timelastdata > (self.beacontime[i] + 300) :
                            #update it
                            self.beacontime[i] = timelastdata
                            self.beaconrssi[i] = rssi
                            rx_count = self.beaconcount[i]
                            self.beaconcount[i]=self.beaconcount[i]+1

                            #if len(beaconevents) > 20:
                            #    beaconevents.pop(0)
                            #beaconevents.append([timelastdata, devid, rssi])
                            self.eventBuffer.add([timelastdata, devid, rssi, rx_count])

                            #print('Updated index {}'.format(i))



                else:
                    anydata = False



    def start_scan(self):
        print('Starting BLE scan')
        #bluetooth =
        self.bluetooth.callback(trigger = Bluetooth.NEW_ADV_EVENT, handler = self.new_adv_event)
        self.bluetooth.init()
        self.bluetooth.start_scan(-1)
