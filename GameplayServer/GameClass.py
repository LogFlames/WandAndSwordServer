# -*- coding: utf-8 -*-

import struct
import time
import socket

class GameClass:
    def __init__(self):
        self.clients = []

        self.debug = False

        self.prints = []

        self.kick_time = 11

        self.udpToSend = []

    def add_client(self, client):
        self.clients.append(client)

    def clean_clients(self):
        for index in range(len(self.clients) - 1, -1, -1):
            if self.clients[index].toBeRemoved:
                del self.clients[index]

    def recv_data(self):
        for client in self.clients:
            if (client.clientSocket == None or client.clientSocket.fileno() == -1 or client.toBeRemoved or time.time() - client.lastPacket > self.kick_time):
                self.prints.append('Removed {} from server due to server-side detect of disconnect, kick command or timeout'.format(client.addr))
                client.toBeRemoved = True
                client.clientSocket.close()
                continue

            gotData = False
            try:
                incoming = client.clientSocket.recv(1024)
                gotData = True
            except:
                pass
            else:
                self.handle_tcp_data(client, incoming)

        """
        0 = ping
        1 = position
        2 = login credentials
        3 = new account credentiales
        4 = server to data base pull credentials request
        5 = username sharing
        6 = player penalty
        7 = Login success
        8 = Attack
        """

    def handle_tcp_data(self, client, data):
        if len(data) == 0:
            self.prints.append('Kicked {} from the server'.format(client.addr))
            client.name = ' '
            for client2 in self.clients:
                if client.clientID == client2.clientID:
                    continue
                data = struct.pack('I', 5) + (' ' + '\x00').encode('utf-8')
                client2.addNetworkItem(0, data)
            client.clientSocket.close()
            client.toBeRemoved = True
            return False

        client.lastPacket = time.time()

        if self.debug:
            self.prints.append("Recv: {} from {} using TCP".format(data, client.addr))

        for part in list(filter(None, data.split(b'\xff\xff\xff\xff'))):
            self.handle_input_part_data(client, part)

    def handle_udp_data(self, data, receivedAddr):
        if len(data) == 0:
            self.print.append('UDP data handeling request : no data given')
            return False

        if self.debug:
            self.prints.append("Recv: {} from the UDP socket using".format(data))

        for part in list(filter(None, data.split(b'\xff\xff\xff\xff'))):
            client = self.get_client_by_id(struct.unpack("I", part[:4])[0])
            if not client:
                continue
            else:
                part = part[4:]

            client.lastPacket = time.time()

            client.UDP_addr = receivedAddr

            self.handle_input_part_data(client, part)

    def handle_input_part_data(self, client, part):
        unpacked_id = struct.unpack('I', part[:4])[0]
        if unpacked_id == 0:
            client.addNetworkItem(0, part)
        elif unpacked_id == 1:
            for client2 in self.clients:
                if client.clientID == client2.clientID:
                    continue
                client2.addNetworkItem(4, part)
        elif unpacked_id == 2 or unpacked_id == 3:
            # 0 == Login success
            # 1 == Login fail
            # 2 == Database down
            data = part[4:].decode('utf-8').strip()

            splitData = list(filter(None, data.split('\x00')))
            if len(splitData) != 2:
                client.addNetworkItem(0, struct.pack('II', 7, 1))
                return

            name, password = splitData

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setblocking(0)
            s.settimeout(1)
            try:
                s.connect(('192.168.10.171', 8060))
            except:
                self.prints.append("Couldn't connect to database.")
                client.addNetworkItem(0, struct.pack('II', 7, 2))
                return

            if unpacked_id == 2:
                s.sendall(("l" + "\x00" + name + "\x00" + password + "\x00").encode("utf-8"))
            elif unpacked_id == 3:
                s.sendall(("c" + "\x00" + name + "\x00" + password + "\x00").encode("utf-8"))
            
            try:
                db_response = s.recv(32)
            except:
                client.addNetworkItem(0, struct.pack('II', 7, 1))
                return

            db_response = struct.unpack('?', db_response)[0]

            success = False
            if not db_response:
                success = False
                self.prints.append('{}: failed to {}'.format(client.addr, ("login" if unpacked_id == 2 else "create account")))
            elif db_response:
                self.prints.append('{}: successful login or account creation. Addr: {}'.format(name, client.addr))
                success = True
                client.name = name

                for client2 in self.clients:
                    if client.clientID == client2.clientID:
                        continue
                    data = struct.pack('I', 5) + (client.name + '\x00').encode('utf-8')
                    client2.addNetworkItem(0, data)

                    data = struct.pack('I', 5) + (client2.name + '\x00').encode('utf-8')
                    client.addNetworkItem(0, data)

            # Not neccecary as client now can read name data directly aftyer login       
            #client.addNetworkItem(2, 0.08)

            client.addNetworkItemLeft(0, struct.pack('II', 7, (0 if success else 1)))

            client.addNetworkItemLeft(0, struct.pack('II', 9, client.clientID))
        else:
            for client2 in self.clients:
                if client.clientID == client2.clientID:
                    continue
                client2.addNetworkItem(0, part)

    def send_data(self):
        for client in self.clients:
            firstMessageSent = True
            if client.calcSleepTime():
                while len(client.networkMessages) > 0 and client.calcSleepTime():
                    typeOfMessage = client.networkTypesOfItem.popleft()
                    networkData = client.networkMessages.popleft()
                    
                    if typeOfMessage == 0:
                        client.send_buffer_to_client(networkData, True)
                    elif typeOfMessage == 1:
                        for client2 in self.clients:
                            if client.clientID == client2.clientID:
                                continue
                            client2.send_buffer_to_client(networkData, True)
                    elif typeOfMessage == 2:
                        client.setSleepTime(networkData)
                    elif typeOfMessage == 3:
                        if firstMessageSent:
                            client.send_buffer_to_client(networkData, True)
                            break
                        else:
                            client.addNetworkItemLeft(typeOfMessage, networkData)
                            break
                    elif typeOfMessage == 4:
                        self.udpToSend.append((client, client.recvMessage[0], True))

                    firstMessageSent = False

    def resend_names(self):
        for client in self.clients:
            for client2 in self.clients:
                if client.clientID == client2.clientID:
                    continue
                data = struct.pack('I', 5) + (client2.name + '\x00').encode('utf-8')
                client.recvMessage.append(data)
                client.recver.append(0)

    def kick_clients(self, clientIDs):
        foundC = False
        for client in self.clients:
            if client.clientID in clientIDs:
                client.toBeRemoved = True
                client.clientSocket.close()
                foundC = True
        return foundC

    def update_clients_debug(self):
        for client in self.clients:
            client.debug = self.debug

    def update_print_request(self):
        for client in self.clients:
            self.prints += client.prints
            client.prints = []

    def get_client_by_addr(self, addr):
        for client in self.clients:
            if addr == client.addr:
                return client
        return False

    def get_client_by_UDP_addr(self, udpAddr):
        if udpAddr == None:
            return False
        for client in self.clients:
            if udpAddr == client.UDPAddr:
                return client
        return None

    def get_client_by_id(self, clientID):
        for client in self.clients:
            if clientID == client.clientID:
                return client
        return False

    def send_client_IDs(self):
        for client in self.clients:
            client.recvMessage.append(struct.pack("II", 9, client.clientID))
            client.recver.append(0)