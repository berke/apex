#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This is the entry point for the application, just a sandbox right now."""

__author__ = 'Jeffrey Phillips Freeman WI2ARD <freemo@gmail.com>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016, Syncleus, Inc. and contributors'

import time
#import serial
import signal
import sys
import kiss.constants
import aprs

#kissinit = [13, 27, 64, 75, 13]
#kissend = [192, 255, 192, 13]


# configure the serial connections (the parameters differs on the device you are connecting to)
#ser = serial.Serial(
#    port='/dev/ttyUSB0',
#    baudrate=38400,
#    parity=serial.PARITY_NONE,
#    stopbits=serial.STOPBITS_ONE,
#    bytesize=serial.EIGHTBITS
#)

aprskiss = aprs.APRSKISS(com_port="/dev/ttyUSB0")
aprskiss.start(kiss.constants.MODE_INIT_W8DED)

def sigint_handler(signal, frame):
    aprskiss.close()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

print("Press ctrl + c at any time to exit")

#After 5 seconds send out a test package.
time.sleep(1)
beacon_frame = {
    'source': 'WI2ARD',
    'destination': 'APRS',
    'path': 'WIDE1-1',
    'text': '!/:=i@;N.G& --G/D R-I-R H24'
}

status_frame = {
    'source': 'WI2ARD',
    'destination': 'APRS',
    'path': 'WIDE1-1',
    'text': '>Robust Packet Radio http://JeffreyFreeman.me'
}

#ser.write(kissinit)

#a = aprs.APRS('WI2ARD', '17582')
#a.connect("noam.aprs2.net".encode('ascii'), "14580".encode('ascii'))
#a.send('WI2ARD>APRS:>Hello World!')

while 1 :
        #out = ''

        # let's wait one second before reading output (let's give device time to answer)
        aprskiss.write(beacon_frame)
        aprskiss.write(status_frame)
        time.sleep(600)
        #while ser.inWaiting() > 0:
        #    out += ser.read(1).decode('utf-8')

        #if out != '':
        #    print(out)

