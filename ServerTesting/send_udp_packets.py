# -- coding: utf-8 --
import socket
import time
import struct

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

host = input("Host: ")
port = int(input("port: "))

while True:
    time.sleep(0.1)

    print("Sending udp packet...")
    udp_socket.sendto(struct.pack("I?I", 7, False, 123), (host, port))