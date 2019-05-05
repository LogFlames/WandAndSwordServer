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
                client.clientSocket.close()
                continue

            gotData = False
            try:
                incoming = client.clientSocket.recv(1024)

                if len(incoming) == 0:
                    print('Kicked {} from the server'.format(client.addr))
                    client.name = ' '
                    for client2 in self.clients:
                        if client.clientID == client2.clientID:
                            continue
                        data = struct.pack('i', 5) + (' ' + '\x00').encode('utf-8')
                        client2.recvMessage.append(data)
                        client2.recver.append(0)
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
                # login 2
                # register 3
                # database and server 4
                # usernames 5
                
                unpacked_id = struct.unpack('B', incoming[:1])[0]
                if unpacked_id == 0:
                    client.recvMessage.append(incoming)
                    client.recver.append(0)
                elif unpacked_id == 2 or unpacked_id == 3:
                    data = incoming[4:].decode('utf-8').strip()

                    splitData = list(filter(None, data.split('\x00')))
                    if len(splitData) != 2:
                        client.recvMessage.append(struct.pack('?', False))
                        client.recver.append(0)
                        continue

                    name, password = splitData

                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setblocking(0)
                    s.settimeout(1)
                    try:
                        s.connect(('192.168.10.171', 8060))
                    except:
                        print("Couldn't connect to database.")
                        client.recvMessage.append(struct.pack('?', False))
                        client.recver.append(0)
                        continue

                    if unpacked_id == 2:
                        s.sendall(("l:" + name + ":" + password + "\n").encode("utf-8"))
                    elif unpacked_id == 3:
                        s.sendall(("c:" + name + ":" + password + "\n").encode("utf-8"))
                    
                    try:
                        db_response = s.recv(32)
                    except:
                        client.recvMessage.append(struct.pack('?', False))
                        client.recver.append(0)
                        continue

                    db_response = struct.unpack('?', db_response)
                    success = False
                    if not db_response:
                        success = False
                    elif db_response:
                        print('{}: successful login or account creation.'.format(name))
                        success = True
                        client.name = name

                        for client2 in self.clients:
                            if client.clientID == client2.clientID:
                                continue
                            data = struct.pack('i', 5) + (client.name + '\x00').encode('utf-8')
                            client2.recvMessage.append(data)
                            client2.recver.append(0)

                            # JUST WORK >:(
                            # Pulling names from other clients
                            data = struct.pack('i', 5) + (client2.name + '\x00').encode('utf-8')
                            client.recvMessage.append(data)
                            client.recver.append(0)
                            
                    client.recvMessage.insert(0, 0.05)
                    client.recver.insert(0, 2)

                    client.recvMessage.insert(0, struct.pack('?', success))
                    client.recver.insert(0, 0)
                else:
                    for client2 in self.clients:
                        if client.clientID == client2.clientID:
                            continue
                        client2.recvMessage.append(incoming)
                        client2.recver.append(0)

    def sendData(self):
        for client in self.clients:
            if client.calcSleepTime():
                if len(client.recvMessage) > 0:
                    if len(client.recver) == 0 or client.recver[0] == 0:
                        client.sendBufferToClient(client.recvMessage[0])
                    elif client.recver[0] == 1:
                        for client2 in self.clients:
                            if client.clientID == client2.clientID:
                                continue
                            client2.sendBufferToClient(client.recvMessage[0])
                    elif client.recver[0] == 2:
                        client.setSleepTime(client.recvMessage[0])
                    del client.recvMessage[0]
                    if len(client.recver) > 0:
                        del client.recver[0]

    def resendNames(self):
        for client in self.clients:
            for client2 in self.clients:
                if client.clientID == client2.clientID:
                    continue
                data = struct.pack('i', 5) + (client2.name + '\x00').encode('utf-8')
                client.recvMessage.append(data)
                client.recver.append(0)

    def kick_clients(self, clientIDs):
        for client in self.clients:
            if client.clientID in clientIDs:
                client.toBeRemoved = True
                client.clientSocket.close()