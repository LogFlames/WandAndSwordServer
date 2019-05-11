# -*- coding: utf-8 -*-

import time

class ClientClass:
    def __init__(self, clientID, connection, addr, debug):
        self.clientID = clientID
        self.addr = addr
        self.clientSocket = connection

        self.name = " "

        self.toBeRemoved = False

        self.recvMessage = []
        self.recver = []

        self.sleepTime = 0

        self.debug = debug

        self.prints = []

        self.lastPacket = time.time() + 11

    def sendToClient(self, msg):
        try:
            self.clientSocket.sendall((msg + '\n').encode('utf-8'))
            if self.debug:
                self.prints.append('Sent {} to {}'.format(msg, self.addr))
        except:
            self.prints.append('Failed to send {} to {}'.format(msg, self.addr))

    def sendBufferToClient(self, buf):
        try:
            self.clientSocket.sendall(buf)
            if self.debug:
                self.prints.append('Sent {} to {}'.format(buf, self.addr))
        except:
            self.prints.append('Failed to send {} to {}'.format(buf, self.addr))

    def setSleepTime(self, delay):
        self.sleepTime = time.time() + delay

    def calcSleepTime(self):
        return self.sleepTime <= time.time()
