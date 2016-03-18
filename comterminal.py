#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This is the entry point for the application, just a sandbox right now."""

__author__ = 'Jeffrey Phillips Freeman WI2ARD <freemo@gmail.com>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016, Syncleus, Inc. and contributors'

import time
import signal
import sys
import kiss.constants
import aprs
import threading
import mysql

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

#a = aprs.APRS('WI2ARD', '17582')
#a.connect("noam.aprs2.net".encode('ascii'), "14580".encode('ascii'))
#a.send('WI2ARD>APRS:>Hello World!')

conn = None
query_write = "INSERT INTO received(source, destination, path, payload) VALUES(%s,%s,%s,%s)"
def kiss_reader(frame):
    try:
        decoded_frame = aprs.util.decode_Frame(frame)
        if conn is not None:
            args_write = (decoded_frame['source'], decoded_frame['destination'], decoded_frame['path'], decoded_frame['text'])
            try:
                cursor = conn.cursor()
                cursor.execute(query_write, args_write)
                conn.commit()
            finally:
                cursor.close()
        formatted_aprs = aprs.util.format_aprs_frame(decoded_frame)
        print("<< " + formatted_aprs)
    except Exception as ex:
        print(ex)
        print("Error Decoding frame:")
        print("\t%s" % frame)

def kiss_reader_thread():
    aprskiss.read(callback=kiss_reader)

try:
    #conn = mysql.connector.connect(host='localhost', database='apex', user='apex')
    #if conn.is_connected() is False:
    #    raise Exception('Could not connect to database')
    threading.Thread(target=kiss_reader_thread)
    while 1 :
        # let's wait one second before reading output (let's give device time to answer)
        aprskiss.write(beacon_frame)
        print(">> " + aprs.util.format_aprs_frame(beacon_frame))
        aprskiss.write(status_frame)
        print(">> " + aprs.util.format_aprs_frame(status_frame))
        time.sleep(600)
except Exception as ex:
    print(ex)
    print("Error running program")
finally:
    if conn is not None:
        conn.close()

