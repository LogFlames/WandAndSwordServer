# -*- coding: utf-8 -*-

import socket

serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ip = input("Ip: ")
port = int(input("Port: "))

serversocket.bind((ip, port))

serversocket.settimeout(0.05)

while True:
    try:
        data, addr = serversocket.recvfrom(2048)
    except:
        pass
    else:
        print("{} : {}".format(data, addr))