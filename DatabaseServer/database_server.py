# -*- coding: utf-8 -*-

import time
import socket
import struct
import hashlib
import os
import configparser
import datetime

from database_server_gui import *

USER_FOLDER = "USERS"

LOG_FILES = "LOGS"

path_to_script = os.path.dirname(__file__)
path_to_users = os.path.join(path_to_script, USER_FOLDER)
path_to_logs = os.path.join(path_to_script, LOG_FILES)

os.makedirs(path_to_users, exist_ok=True)
os.makedirs(path_to_logs, exist_ok=True)

log_file = open(os.path.join(path_to_logs, "Log-{}.txt".format(str(datetime.datetime.today().replace(microsecond=0)).replace(":", ";"))), "a")

def print_gui_with_log(msg):
    print_gui(msg)
    log_file.write(msg + "\n")

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
    print_gui_with_log(" ")
    print_gui_with_log("Failed to create initial socket. Exiting: {}".format(datetime.datetime.now()))
    log_file.close()
    exit()

def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
    except:
        print_gui_with_log('No internet connection.')
        print_gui_with_log('Try reconnection and restarting the server')
        print_gui_with_log("Launching into default host: 'localhost'")
        return 'localhost'

    return s.getsockname()[0]

host = getIP()

port = 8060
try:
    serverSocket.bind((host, port))
    print_gui_with_log(' ')
    print_gui_with_log('Server is running on --> {}:{}'.format(host, str(port)))
    print_gui_with_log(' ')
except:
    print_gui_with_log('Port {} is already in use on the host machine, free the port and try again.'.format(str(port)))

serverSocket.listen(5)
serverSocket.setblocking(0)
serverSocket.settimeout(0.05)

running = True

print_gui_with_log("Server started: {}".format(datetime.datetime.now()))

while running:
    screen.update()
    if reqExit():
        running = False
    try:
        client, addr = serverSocket.accept()
    except:
        client = False

    if client:
        print_gui_with_log('Incomming connection from {}'.format(addr))
        client.setblocking(0)
        client.settimeout(1)

        try:
            incoming = client.recv(1024)

            if len(incoming) == 0:
                client.close()
                continue
        except:
            client.sendall(struct.pack('?', False))
            client.close()
            continue

        if len(incoming.decode('utf-8').strip().split(":")) != 3:
            client.sendall(struct.pack('?', False))
            client.close()
            continue

        success = False

        typ, name, pasw = incoming.decode('utf-8').strip().split(":")

        if typ.startswith("c"):
            if addUser(name, pasw):
                success = True
                client.sendall(struct.pack('?', True))
            else:
                client.sendall(struct.pack('?', False))
        elif typ.startswith("l"):
            if checkLogin(name, pasw):
                success = True
                client.sendall(struct.pack('?', True))
            else:
                client.sendall(struct.pack('?', False))
        else:
            print_gui_with_log("{} tried to send invalid command: {}".format(addr, incoming))
        
        print_gui_with_log('{} tried to login with {} and {}'.format(addr, name, pasw))
        print_gui_with_log('Result of login: {}'.format(success))

        client.close()

serverSocket.close()

print_gui_with_log(" ")
print_gui_with_log("Server closed: {}".format(datetime.datetime.now()))

log_file.close()