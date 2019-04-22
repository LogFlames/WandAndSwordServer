# -*- coding: utf-8 -*-

import struct
import time
from datetime import datetime

class GameClass:
    def __init__(self, bufOrMsg):
        self.clients = []
        self.bufOrMsg = bufOrMsg

    def addClient(self, client):
        self.clients.append(client)

    def cleanClients(self):
        for index in range(len(self.clients) - 1, -1, -1):
            if self.clients[index].toBeRemoved:
                del self.clients[index]

    def recvData(self):
        for client in self.clients:
            if client.clientSocket == None or client.clientSocket.fileno() == -1 or client.toBeRemoved:
                print('Removed {} from server due to server-side detect of disconnect or kick command'.format(client.addr))
                client.toBeRemoved = True
                continue

            gotData = False
            try:
                incoming = client.clientSocket.recv(1024)

                if len(incoming) == 0:
                    print('Kicked {} from the server'.format(client.addr))
                    client.clientSocket.close()
                    client.toBeRemoved = True
                else:
                    gotData = True

            except:
                gotData = False

            if gotData:
                if self.bufOrMsg == 'buf':
                    # unpack struct
                    # ping 0
                    # pos 1
                    
                    unpacked_id = struct.unpack('B', incoming[:1])[0]
                    if unpacked_id == 0:
                        client.recvMessage = incoming
                        client.recver = 0
                    else:
                        client.recvMessage = incoming
                        client.recver = 1
                elif self.bufOrMsg == 'msg':
                    couldDecode = False
                    try:
                        incoming = incoming.decode('utf-8').strip()
                        couldDecode = True
                    except:
                        print("Data {} couldn't be decoded by standard utf-8, check encodeing fucntion for adnormalities".format(incoming))

                    if couldDecode:
                        client.recvMessage = incoming

    def sendData(self):
        for client in self.clients:
            if client.recvMessage != '':
                if client.recver == 0:
                    client.sendBufferToClient(client.recvMessage)
                elif client.recvMessage == 1:
                    for client2 in self.clients:
                        if client.clientID == client2.clientID:
                            continue
                        if self.bufOrMsg == 'buf':
                            client2.sendBufferToClient(client.recvMessage)
                        if self.bufOrMsg == 'msg':
                            client2.sendToClient(client.recvMessage)
                client.recvMessage = ''
