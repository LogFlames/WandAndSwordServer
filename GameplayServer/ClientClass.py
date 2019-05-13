# -*- coding: utf-8 -*-

import time
import struct
import socket
from collections import deque

class ClientClass:
    def __init__(self, clientID, connection, addr, debug):
        self.clientID = clientID
        self.addr = addr
        self.UDPAddr = None
        self.clientSocket = connection

        self.name = " "

        self.toBeRemoved = False

        # 0 == send to self
        # 1 == send to everyone else
        # 2 == sleep
        # 3 == send to self alone
        # 4 == send to self udp

        self.networkMessages = deque()
        self.networkTypesOfItem = deque()

        self.sleepTime = 0

        self.debug = debug

        self.prints = []

        self.lastPacket = time.time() + 11

    def addNetworkItem(self, typeOfItem, networkMessage):
        self.networkTypesOfItem.append(typeOfItem)
        self.networkMessages.append(networkMessage)

    def addNetworkItemLeft(self, typeOfItem, networkMessage):
        self.networkTypesOfItem.appendleft(typeOfItem)
        self.networkMessages.appendleft(networkMessage)

    def send_buffer_to_client(self, buf, addNum):
        try:
            if addNum:
                buf = struct.pack("I", 4294967295) + buf # 2**32-1     b'\xff\xff\xff\xff'
            self.clientSocket.sendall(buf)
            if self.debug:
                self.prints.append('Sent {} to {}'.format(buf, self.addr))
        except:
            self.prints.append('Failed to send {} to {}'.format(buf, self.addr))

    def setSleepTime(self, delay):
        self.sleepTime = time.time() + delay

    def calcSleepTime(self):
        return self.sleepTime <= time.time()
