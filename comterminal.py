#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This is the entry point for the application, just a sandbox right now."""
import aprs.aprs_kiss

__author__ = 'Jeffrey Phillips Freeman WI2ARD <freemo@gmail.com>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016, Syncleus, Inc. and contributors'

import time
import signal
import sys
import kiss.constants
import aprs
import aprs.util
import threading

aprskiss = aprs.aprs_kiss.AprsKiss(com_port="/dev/ttyUSB1", baud=9600)
aprskiss.start(kiss.constants.MODE_INIT_KENWOOD_D710)
#aprskiss = aprs.APRSKISS(com_port="/dev/ttyUSB0", baud=38400)
#aprskiss.start(kiss.constants.MODE_INIT_W8DED)

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
    'text': list(b'!/:=i@;N.G& --G/D R-I-R H24')
}

status_frame = {
    'source': 'WI2ARD',
    'destination': 'APRS',
    'path': 'WIDE1-1',
    'text': list(b'>Robust Packet Radio http://JeffreyFreeman.me')
}

#a = aprs.APRS('WI2ARD', '17582')
#a.connect("noam.aprs2.net".encode('ascii'), "14580".encode('ascii'))
#a.send('WI2ARD>APRS:>Hello World!')

def kiss_reader(decoded_frame):
    formatted_aprs = aprs.util.format_aprs_frame(decoded_frame)
    print("<< " + formatted_aprs)

def kiss_reader_thread():
    print("Begining kiss reader thread...")
    while 1:
        frame = aprskiss.read()
        if frame is not None and len(frame):
            kiss_reader(frame)
        else:
            time.sleep(1)


threading.Thread(target=kiss_reader_thread, args=()).start()
while 1 :
    # let's wait one second before reading output (let's give device time to answer)
    aprskiss.write(beacon_frame)
    print(">> " + aprs.util.format_aprs_frame(beacon_frame))
    aprskiss.write(status_frame)
    print(">> " + aprs.util.format_aprs_frame(status_frame))
    time.sleep(600)

