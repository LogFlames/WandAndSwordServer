# -*- coding: utf-8 -*-

import struct
import time
from datetime import datetime
import socket
import itertools

class GameClass:
    def __init__(self):
        self.clients = []

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
                # unpack struct
                # ping 0
                # pos 1
                
                unpacked_id = struct.unpack('B', incoming[:1])[0]
                if unpacked_id == 0:
                    client.recvMessage = incoming
                    client.recver = 0
                elif unpacked_id == 2 or unpacked_id == 3:
                    client.recver = 0
                    data = incoming[4:].decode('utf-8').strip()

                    splitData = list(filter(None, data.split('\x00')))
                    if len(splitData) != 2:
                        client.recvMessage = struct.pack('?', False)
                        continue

                    name, password = splitData

                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setblocking(0)
                    s.settimeout(1)
                    try:
                        s.connect(('192.168.10.171', 8060))
                    except:
                        print("Couldn't connect to database.")

                    if unpacked_id == 2:
                        s.sendall(("l:" + name + ":" + password + "\n").encode("utf-8"))
                    elif unpacked_id == 3:
                        s.sendall(("c:" + name + ":" + password + "\n").encode("utf-8"))
                    
                    try:
                        db_response = s.recv(32)
                    except:
                        client.recvMessage = struct.pack('?', False)
                        continue

                    db_response = db_response.decode('utf-8').strip()
                    success = False
                    if db_response == '0':
                        success = False
                    elif db_response == '1':
                        print('{}: successful login or account creation.'.format(name))
                        success = True
                        client.name = name

                    client.recvMessage = struct.pack('?', success)
                else:
                    client.recvMessage = incoming
                    client.recver = 1

    def sendData(self):
        for client in self.clients:
            if client.recvMessage != '':
                if client.recver == 0:
                    client.sendBufferToClient(client.recvMessage)
                elif client.recver == 1:
                    for client2 in self.clients:
                        if client.clientID == client2.clientID:
                            continue
                        client2.sendBufferToClient(client.recvMessage)
                client.recvMessage = ''
            if client.name != client.lastName:
                client.lastName = client.name

                name = bytes(client.name, 'utf-8')
                # THIS DOESN'T WORK
                data = struct.pack('i' + 'c' * len(name), 5, *name)
                for client2 in self.clients:
                    if client.clientID == client2.clientID:
                        continue
                    client2.sendBufferToClient(data)
