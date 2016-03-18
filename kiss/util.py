#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utilities for the KISS Python Module."""

__author__ = 'Jeffrey Phillips Freeman WI2ARD <freemo@gmail.com>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016, Syncleus, Inc. and contributors'


import kiss.constants


def escape_special_codes(raw_code_bytes):
    """
    Escape special codes, per KISS spec.

    "If the FEND or FESC codes appear in the data to be transferred, they
    need to be escaped. The FEND code is then sent as FESC, TFEND and the
    FESC is then sent as FESC, TFESC."
    - http://en.wikipedia.org/wiki/KISS_(TNC)#Description
    """
    encoded_bytes = []
    for raw_code_byte in raw_code_bytes:
        if raw_code_byte is kiss.constants.FESC:
            encoded_bytes += kiss.constants.FESC_TFESC
        elif raw_code_byte is kiss.constants.FEND:
            encoded_bytes += kiss.constants.FESC_TFEND
        else:
            encoded_bytes += [raw_code_byte];
    return encoded_bytes


def extract_ui(frame):
    """
    Extracts the UI component of an individual frame.

    :param frame: APRS/AX.25 frame.
    :type frame: str
    :returns: UI component of frame.
    :rtype: str
    """
    start_ui = frame.split(
        ''.join([kiss.constants.FEND, kiss.constants.DATA_FRAME]))
    end_ui = start_ui[0].split(''.join([kiss.constants.SLOT_TIME, chr(0xF0)]))
    return ''.join([chr(ord(x) >> 1) for x in end_ui[0]])


def strip_df_start(frame):
    """
    Strips KISS DATA_FRAME start (0x00) and newline from frame.

    :param frame: APRS/AX.25 frame.
    :type frame: str
    :returns: APRS/AX.25 frame sans DATA_FRAME start (0x00).
    :rtype: str
    """
    return frame.lstrip(kiss.constants.DATA_FRAME).strip()
