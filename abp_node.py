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
import binascii
import struct
import time
import config
import ujson

from ble_scanner import BLEScanner


# initialize LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

# create an ABP authentication params
dev_addr = struct.unpack(">l", binascii.unhexlify('27211441'))[0]
nwk_swkey = binascii.unhexlify('11B362F2207544614C4339337C151125')
app_swkey = binascii.unhexlify('333ED2330C7D1DC822E1224A1A112A11')


#module 1
#dev_addr = struct.unpack(">l", binascii.unhexlify('26011581'))[0]
#nwk_swkey = binascii.unhexlify('42B362F6A075C06142C4349A7C1588A5')
#app_swkey = binascii.unhexlify('B43ED2880C7D1DC862E1DC4A1A162A90')

#module 2
#dev_addr = struct.unpack(">l", binascii.unhexlify('26011DF3'))[0]
#nwk_swkey = binascii.unhexlify('733126B12A818748C54DA3EA2320222D')
#app_swkey = binascii.unhexlify('D80038DCD0DFB77B9863E9DC6BA71B08')


# remove all the non-default channels
for i in range(3, 16):
    lora.remove_channel(i)

# set the 3 default channels to the same frequency
lora.add_channel(0, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)
lora.add_channel(1, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)
lora.add_channel(2, frequency=config.LORA_FREQUENCY, dr_min=0, dr_max=5)

# join a network using ABP (Activation By Personalization)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, config.LORA_NODE_DR)

# make the socket non-blocking
s.setblocking(False)


scanner = BLEScanner(64)
scanner.start_scan()


for i in range (0):
    pkt = b'PKT #' + bytes([i])
    print('Sending:', pkt)
    s.send(pkt)
    time.sleep(4)
    rx, port = s.recvfrom(256)
    if rx:
        print('Received: {}, on port: {}'.format(rx, port))
    time.sleep(10)




while True:

    if not scanner.eventBuffer.isEmpty():
        x = scanner.eventBuffer.remove()

        msg_up = {}
        msg_up["T"] = x[0]
        msg_up["M"] = x[1]
        msg_up["R"] = x[2]
        msg_up["C"] = x[3]

        s.send(ujson.dumps(msg_up))
        print('Sent MAC Info')
        print(ujson.dumps(msg_up))

        time.sleep(1)
