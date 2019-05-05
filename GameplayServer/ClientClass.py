# -*- coding: utf-8 -*-

import time

class ClientClass:
    def __init__(self, clientID, connection, addr):
        self.clientID = clientID
        self.addr = addr
        self.clientSocket = connection

        self.name = " "

        self.toBeRemoved = False

        self.recvMessage = []
        self.recver = []

        self.sleepTime = 0

    def sendToClient(self, msg):
        try:
            self.clientSocket.sendall((msg + '\n').encode('utf-8'))
            #print('Sent {} to {}'.format(msg, self.addr))
        except:
            print('Failed to send {} to {}'.format(msg, self.addr))

    def sendBufferToClient(self, buf):
        try:
            self.clientSocket.sendall(buf)
            #print('Sent {} to {}'.format(buf, self.addr))
        except:
            print('Failed to send {} to {}'.format(buf, self.addr))

    def setSleepTime(self, delay):
        self.sleepTime = time.time() + delay

    def calcSleepTime(self):
        return self.sleepTime <= time.time()
