# -*- coding: utf-8 -*-

import socket

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ip = input("Ip: ")
port = int(input("Port: "))

serversocket.bind((ip, port))

serversocket.listen(5)
serversocket.settimeout(0.05)

connections = []

while True:
    try:
        s, addr = serversocket.accept()
    except:
        pass
    else:
        connections.append((s, addr))

    for s, addr in connections:
        try:
            data = s.recv(2048)
        except:
            pass
        else:
            print(data.decode('utf-8'))