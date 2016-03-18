#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Constants for KISS Python Module."""

__author__ = 'Jeffrey Phillips Freeman WI2ARD <freemo@gmail.com>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016, Syncleus, Inc. and contributors'


import logging


LOG_LEVEL = logging.DEBUG
LOG_FORMAT = ('%(asctime)s %(levelname)s %(name)s.%(funcName)s:%(lineno)d'
              ' - %(message)s')

SERIAL_TIMEOUT = 0.01
READ_BYTES = 1000

# KISS Special Characters
# http://en.wikipedia.org/wiki/KISS_(TNC)#Special_Characters
FEND = 0xC0
FESC = 0xDB
TFEND = 0xDC
TFESC = 0xDD

# "FEND is sent as FESC, TFEND"
FESC_TFEND = [FESC] + [TFEND]

# "FESC is sent as FESC, TFESC"
FESC_TFESC = [FESC] + [TFESC]

# KISS Command Codes
# http://en.wikipedia.org/wiki/KISS_(TNC)#Command_Codes
DATA_FRAME = 0x00
TX_DELAY = 0x01
PERSISTENCE = 0x02
SLOT_TIME = 0x03
TX_TAIL = 0x04
FULL_DUPLEX = 0x05
SET_HARDWARE = 0x06
RETURN = 0xFF

DEFAULT_KISS_CONFIG_VALUES = {
    'TX_DELAY': 40,
    'PERSISTENCE': 63,
    'SLOT_TIME': 20,
    'TX_TAIL': 30,
    'FULL_DUPLEX': 0,
    }

#This command will exit KISS mode
MODE_END = [192, 255, 192, 13]
# This will start kiss on a W8DED or LINK>.<NORD firmware
MODE_INIT_W8DED = [13, 27, 64, 75, 13]
MODE_INIT_LINKNORD = MODE_INIT_W8DED