import time
import socket
import struct
from collections import deque

class ClientClass:
    def __init__(self, clientID, connection, addr):
        self.clientID = clientID
        self.addr = addr
        self.clientSocket = connection
        self.UDPAddr = None
        self.name = ""
        self.lastPacket = time.time() + 11   
        self.des = 0
        self.sleepTime = 0

        # 0 = ping     

        def send_buffer_to_client(self, buff, addNum):
            try:
                buff = struct.pack("I", self.des)
                self.clientSocket.sendall(buff)
            except:
                print("Failed to send {} to {}".format(buff, self.addr))