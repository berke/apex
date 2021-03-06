#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""APRS Internet Service Class Definitions"""

__author__ = 'Jeffrey Phillips Freeman WI2ARD <freemo@gmail.com>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016, Syncleus, Inc. and contributors'

import logging
import socket
import requests
import aprs.constants
import time


class AprsInternetService(object):

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

        self.full_auth = ' '.join([self._auth, 'filter', aprs_filter])

        self.server = server
        self.port = port
        self.aprsis_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.aprsis_sock.connect((server, port))
        self.logger.info('Connected to server=%s port=%s', server, port)
        self.logger.debug('Sending full_auth=%s', self.full_auth)
        self.aprsis_sock.sendall((self.full_auth + '\n\r').encode('ascii'))

    def send(self, frame, headers=None, protocol='TCP'):
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
            'message=%s headers=%s protocol=%s', str(frame), headers, protocol)

        if 'TCP' in protocol:
            self.logger.debug('sending message=%s', str(frame))
            # message = frame['source'].encode('ascii') + b">" + frame['destination'].encode('ascii') + aprs.util.format_path(frame['path']).encode('ascii') + b":" + frame['text'] + b'\n\r'
            # TODO: simplify this
            message = bytearray()
            for frame_chr in aprs.util.format_aprs_frame(frame):
                message.append(ord(frame_chr))
            message_sent = False
            while not message_sent:
                try:
                    self.aprsis_sock.sendall(message)
                    message_sent = True
                except (ConnectionResetError, BrokenPipeError) as ex:
                    #connection reset wait a second then try again
                    time.sleep(1)
                    self.aprsis_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.aprsis_sock.connect((self.server, self.port))
                    self.aprsis_sock.sendall((self.full_auth + '\n\r').encode('ascii'))
            return True
        elif 'HTTP' in protocol:
            content = "\n".join([self._auth, aprs.util.format_aprs_frame(frame)])
            headers = headers or aprs.constants.APRSIS_HTTP_HEADERS
            result = requests.post(self._url, data=content, headers=headers)
            return 204 in result.status_code
        elif 'UDP' in protocol:
            content = "\n".join([self._auth, aprs.util.format_aprs_frame(frame)])
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