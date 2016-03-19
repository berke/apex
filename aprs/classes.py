#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Class Definitions"""

__author__ = 'Jeffrey Phillips Freeman WI2ARD <freemo@gmail.com>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016, Syncleus, Inc. and contributors'


import logging
import logging.handlers
import socket
import kiss
import kiss.constants
import requests
import aprs.constants
import aprs.util


class APRS(object):

    """APRS Object."""

    logger = logging.getLogger(__name__)
    logger.setLevel(aprs.constants.LOG_LEVEL)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(aprs.constants.LOG_LEVEL)
    console_handler.setFormatter(aprs.constants.LOG_FORMAT)
    logger.addHandler(console_handler)
    logger.propagate = False

    def __init__(self, user, password='-1', input_url=None):
        self.user = user
        self._url = input_url or aprs.constants.APRSIS_URL
        self._auth = ' '.join(
            ['user', user, 'pass', password, 'vers', 'APRS Python Module'])
        self.aprsis_sock = None

    def connect(self, server=None, port=None, aprs_filter=None):
        """
        Connects & logs in to APRS-IS.

        :param server: Optional alternative APRS-IS server.
        :param port: Optional APRS-IS port.
        :param filter: Optional filter to use.
        :type server: str
        :type port: int
        :type filte: str
        """
        server = server or aprs.constants.APRSIS_SERVER
        port = port or aprs.constants.APRSIS_FILTER_PORT
        aprs_filter = aprs_filter or '/'.join(['p', self.user])

        full_auth = ' '.join([self._auth, 'filter', aprs_filter])

        self.aprsis_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.aprsis_sock.connect((server, int(port)))
        self.logger.info('Connected to server=%s port=%s', server, port)
        self.logger.debug('Sending full_auth=%s', full_auth)
        self.aprsis_sock.sendall((full_auth + '\n\r').encode('ascii'))

    def send(self, message, headers=None, protocol='TCP'):
        """
        Sends message to APRS-IS.

        :param message: Message to send to APRS-IS.
        :param headers: Optional HTTP headers to post.
        :param protocol: Protocol to use: One of TCP, HTTP or UDP.
        :type message: str
        :type headers: dict

        :return: True on success, False otherwise.
        :rtype: bool
        """
        self.logger.debug(
            'message=%s headers=%s protocol=%s', message, headers, protocol)

        if 'TCP' in protocol:
            self.logger.debug('sending message=%s', message)
            self.aprsis_sock.sendall((message + '\n\r').encode('ascii'))
            return True
        elif 'HTTP' in protocol:
            content = "\n".join([self._auth, message])
            headers = headers or aprs.constants.APRSIS_HTTP_HEADERS
            result = requests.post(self._url, data=content, headers=headers)
            return 204 in result.status_code
        elif 'UDP' in protocol:
            content = "\n".join([self._auth, message])
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(
                content,
                (aprs.constants.APRSIS_SERVER, aprs.constants.APRSIS_RX_PORT)
            )
            return True

    def receive(self, callback=None):
        """
        Receives from APRS-IS.

        :param callback: Optional callback to deliver data to.
        :type callback: func
        """
        recvd_data = ''

        try:
            while 1:
                recv_data = self.aprsis_sock.recv(aprs.constants.RECV_BUFFER)

                if not recv_data:
                    break

                recvd_data += recv_data

                self.logger.debug('recv_data=%s', recv_data.strip())

                if recvd_data.endswith('\r\n'):
                    lines = recvd_data.strip().split('\r\n')
                    recvd_data = ''
                else:
                    lines = recvd_data.split('\r\n')
                    recvd_data = str(lines.pop(-1))

                for line in lines:
                    if line.startswith('#'):
                        if 'logresp' in line:
                            self.logger.debug('logresp=%s', line)
                    else:
                        self.logger.debug('line=%s', line)
                        if callback:
                            callback(line)

        except socket.error as sock_err:
            self.logger.error(sock_err)
            raise


class APRSKISS(kiss.KISS):

    """APRS interface for KISS serial devices."""

    def write(self, frame):
        """Writes APRS-encoded frame to KISS device.

        :param frame: APRS frame to write to KISS device.
        :type frame: dict
        """
        encoded_frame = APRSKISS.__encode_frame(frame)
        super(APRSKISS, self).write(encoded_frame)

    @staticmethod
    def __encode_frame(frame):
        """
        Encodes an APRS frame-as-dict as a KISS frame.

        :param frame: APRS frame-as-dict to encode.
        :type frame: dict

        :return: KISS-encoded APRS frame.
        :rtype: list
        """
        enc_frame = APRSKISS.__encode_callsign(APRSKISS.__parse_identity_string(frame['destination'])) + APRSKISS.__encode_callsign(APRSKISS.__parse_identity_string(frame['source']))
        for p in frame['path'].split(','):
            enc_frame += APRSKISS.__encode_callsign(APRSKISS.__parse_identity_string(p))

        return enc_frame[:-1] + [enc_frame[-1] | 0x01] + [kiss.constants.SLOT_TIME] + [0xf0] + frame['text']

    @staticmethod
    def __encode_callsign(callsign):
        """
        Encodes a callsign-dict within a KISS frame.

        :param callsign: Callsign-dict to encode.
        :type callsign: dict

        :return: KISS-encoded callsign.
        :rtype: list
        """
        call_sign = callsign['callsign']

        enc_ssid = (callsign['ssid'] << 1) | 0x60

        if '*' in call_sign:
            call_sign = call_sign.replace('*', '')
            enc_ssid |= 0x80

        while len(call_sign) < 6:
            call_sign = ''.join([call_sign, ' '])

        encoded = []
        for p in call_sign:
            encoded += [ord(p) << 1]
    #    encoded = ''.join([chr(ord(p) << 1) for p in call_sign])
        return encoded + [enc_ssid]

    @staticmethod
    def __parse_identity_string(identity_string):
        """
        Creates callsign-as-dict from callsign-as-string.

        :param identity_string: Callsign-as-string (with or without ssid).
        :type raw_callsign: str

        :return: Callsign-as-dict.
        :rtype: dict
        """
        if '-' in identity_string:
            call_sign, ssid = identity_string.split('-')
        else:
            call_sign = identity_string
            ssid = 0
        return {'callsign': call_sign, 'ssid': int(ssid)}