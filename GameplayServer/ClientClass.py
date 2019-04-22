# -*- coding: utf-8 -*-

class ClientClass:
    def __init__(self, clientID, connection, addr):
        self.clientID = clientID
        self.addr = addr
        self.clientSocket = connection

        self.name = ""
        self.lastName = ""

        self.toBeRemoved = False

        self.recvMessage = ''
        
        self.recver = 1

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
