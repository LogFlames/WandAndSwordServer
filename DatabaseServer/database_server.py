# -*- coding: utf-8 -*-

import time
import socket
import struct
import hashlib
import os
import configparser

from database_server_gui import *

USER_FOLDER = "USERS"

path_to_script = os.path.dirname(__file__)
path_to_users = os.path.join(path_to_script, USER_FOLDER)

def addUser(name, password):
    foundFile = False
    try:
        with open(os.path.join(path_to_users, name + ".ini"), "r"):
            foundFile = True
    except:
        foundFile = False
    
    if foundFile:
        return False

    with open(os.path.join(path_to_users, name + ".ini"), "w+") as f:
        with open(os.path.join(path_to_script, "default.ini"), "r") as default_ini_file:
            for line in default_ini_file:
                f.write(line)
    
    config = configparser.ConfigParser()
    config.read(os.path.join(path_to_users, name + ".ini"))

    config['credentials']['password'] = password

    with open(os.path.join(path_to_users, name + ".ini"), 'w') as configfile:
        config.write(configfile)
    
    return True

def checkLogin(name, password):
    try:
        with open(os.path.join(path_to_users, name + ".ini"), "r"):
            foundFile = True
    except:
        foundFile = False
    
    if not foundFile:
        return False

    config = configparser.ConfigParser()
    config.read(os.path.join(path_to_users, name + ".ini"))

    if config['credentials']['password'] == password:
        return True
    return False


try:
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print_gui("Failed to create initial socket. Exiting")
    exit()

def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
    except:
        print_gui('No internet connection.')
        print_gui('Try reconnection and restarting the server')
        print_gui("Launching into default host: 'localhost'")
        return 'localhost'

    return s.getsockname()[0]

host = getIP()

port = 8060
try:
    serverSocket.bind((host, port))
    print_gui(' ')
    print_gui('Server is running on --> {}:{}'.format(host, str(port)))
    print_gui(' ')
except:
    print_gui('Port {} is already in use on the host machine, free the port and try again.'.format(str(port)))

serverSocket.listen(5)
serverSocket.setblocking(0)
serverSocket.settimeout(0.05)

running = True

while running:
    screen.update()
    if reqExit():
        running = False
    try:
        client, addr = serverSocket.accept()
    except:
        client = False

    if client:
        print_gui('Incomming connection from {}'.format(addr))
        client.setblocking(0)
        client.settimeout(1)

        try:
            incoming = client.recv(1024)

            if len(incoming) == 0:
                client.close()
                continue
        except:
            client.sendall(("0" + "\n").encode('utf-8'))
            client.close()
            continue

        if len(incoming.decode('utf-8').strip().split(":")) != 3:
            client.sendall(("0" + "\n").encode('utf-8'))
            client.close()
            continue

        success = False

        typ, name, pasw = incoming.decode('utf-8').strip().split(":")

        if typ.startswith("c"):
            if addUser(name, pasw):
                success = True
                client.sendall(("1" + "\n").encode('utf-8'))
            else:
                client.sendall(("0" + "\n").encode('utf-8'))
        elif typ.startswith("l"):
            if checkLogin(name, pasw):
                success = True
                client.sendall(("1" + "\n").encode('utf-8'))
            else:
                client.sendall(("0" + "\n").encode('utf-8'))
        else:
            print_gui("{} tried to send invalid command: {}".format(addr, incoming))
        
        print_gui('{} tried to login with {} and {}'.format(addr, name, pasw))
        print_gui('Result of login: {}'.format(success))

        client.close()

serverSocket.close()