# -*- coding: utf-8 -*-

import time
import socket
import struct
import hashlib
import os
import configparser
import datetime
import hashlib
import threading
import queue

from database_server_gui import *

USER_FOLDER = "USERS"

LOG_FILES = "LOGS"

path_to_script = os.path.dirname(__file__)
path_to_users = os.path.join(path_to_script, USER_FOLDER)
path_to_logs = os.path.join(path_to_script, LOG_FILES)

os.makedirs(path_to_users, exist_ok=True)
os.makedirs(path_to_logs, exist_ok=True)

session_temp = str(int(time.time()))

SESSION_ID = session_temp[len(session_temp) - 10:]

log_file = open(os.path.join(path_to_logs, "Log-database-server-{}-{}.txt".format(SESSION_ID, str(datetime.datetime.today().replace(microsecond=0)).replace(":", ";"))), "a")

serverSocket = None

def print_gui_with_log(msg):
    log_file.write(msg + "\n")
    print_gui(msg)

runningLogFileThread = True
reloadLogfileThreadOpen = False

def reload_log_file(timeInterval):
    global log_file
    global reloadLogfileThreadOpen

    reloadLogfileThreadOpen = True

    print_gui_with_log('Logfile will reload every {} seconds'.format(str(timeInterval)))

    while runningLogFileThread:
        waitedTime = 0
        while waitedTime < timeInterval:
            waitedTime += 0.5
            if not runningLogFileThread:
                reloadLogfileThreadOpen = False
                return
            time.sleep(0.5)

        if runningLogFileThread:
            print_gui_with_log('Reloading logfile...')

            log_file.close()
            log_file = open(os.path.join(path_to_logs, "Log-gameplay-server-{}-{}.txt".format(SESSION_ID, str(datetime.datetime.today().replace(microsecond=0)).replace(":", ";"))), "a")

            print_gui_with_log('New logfile started...')

    reloadLogfileThreadOpen = False

def addUser(name, password):
    if checkFile(name):
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

def checkFile(name):
    return os.path.exists(os.path.join(path_to_users, name + ".ini"))

def checkLogin(name, password):
    if not checkFile(name):
        return False

    config = configparser.ConfigParser()
    config.read(os.path.join(path_to_users, name + ".ini"))

    if config['credentials']['password'] == password:
        return True
    return False

def deleteUser(name):
    if checkFile(name):
        os.remove(os.path.join(path_to_users, name + ".ini"))
        return True
    else:
        return False

def getUserInfo(name):
    if checkFile(name):
        with open(os.path.join(path_to_users, name + ".ini"), "r") as f:
            for line in f:
                yield line

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

def bindServer(hst="ip"):
    global serverSocket

    if hst == "l" or hst == "localhost":
        host = "localhost"
    elif hst == "ip":
        host = getIP()
    else:
        print_gui_with_log("Unknown requested serverbind Mode: {}".format(hst))
        return

    try:
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print_gui_with_log(" ")
        print_gui_with_log("Failed to create initial socket. Exiting: {}".format(datetime.datetime.now()))
        log_file.close()
        exit()


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

bindServer()

running = True

print_gui_with_log('Starting logfile reload thread')
reloadLogThread = threading.Thread(target=reload_log_file, args=(7200,), daemon=True)
reloadLogThread.start()
print_gui_with_log('Logfile reload thread started')
print_gui_with_log(' ')

print_gui_with_log("Server started: {}".format(datetime.datetime.now()))

while running:
    if reqExitFunc():
        print_gui_with_log("Exiting program, window closed requested.")
        running = False
        continue

    update_computer_info()
    process_print_queue()
    screen.update()

    for command in getCommands():
        if command == "help" or command == "?":
            print_gui("Help menu:")
            print_gui("help - ? - Opens this menu")
            print_gui("exit - stops the serversocket and program")
            print_gui("delete_user:(name) - Deletes a user from the system. Example: 'delete_user:Log'")
            print_gui("check_file:(name) - Check if file exists. Example: 'check_file:Log'")
            print_gui("user_info:(name) - Prints all info about a user. Example: 'check_user:Log'")
            print_gui("rebind_server:(mode) - Reopenes the server in new mode. Avaiable modes: [ip, localhost]")
            print_gui(" ")
        elif command == "exit":
            print_gui_with_log(">>> {}".format(command))
            print_gui_with_log(" ")
            running = False
        elif command.startswith("delete_user:"):
            print_gui_with_log(">>> {}".format(command))
            if deleteUser(command[12:]):
                print_gui_with_log("User '{}' successfully deleted from system.".format(command[12:]))
            else:
                print_gui_with_log("Couldn't delete user '{}' from database".format(command[12:]))
            print_gui_with_log(" ")
        elif command.startswith("check_file:"):
            print_gui_with_log(">>> {}".format(command))
            command = command[11:]
            if checkFile(command):
                print_gui_with_log("Userfile '{}.ini' successfully found in database.".format(command))
            else:
                print_gui_with_log("Couldn't find userfile '{}.ini' in database".format(command))
            print_gui_with_log(" ")
        elif command.startswith("user_info:"):
            print_gui_with_log(">>> {}".format(command))
            command = command[10:]
            if checkFile(command):
                print_gui_with_log("User info '{}': ".format(command))
                for line in getUserInfo(command):
                    print_gui_with_log(line)
                print_gui_with_log(" ")
            else:
                print_gui_with_log("Couldn't find userfile '{}'".format(command))
        elif command.startswith("rebind_server:"):
            print_gui_with_log(">>> {}".format(command))
            command = command[14:]
            bindServer(command)
        else:
            print_gui("Unknown command, type help to open available commands.")

    try:
        client, addr = serverSocket.accept()
    except:
        client = False

    if client:
        addLoginRequest()

        print_gui_with_log('Incomming connection from {}'.format(addr))
        client.setblocking(0)
        client.settimeout(1)

        try:
            incoming = client.recv(1024)

            if len(incoming) == 0:
                print_gui_with_log("{}'s recieved message was not readable.".format(addr))
                client.close()
                continue
        except:
            print_gui_with_log("{} didn't send any recievable message.".format(addr))
            client.sendall(struct.pack('?', False))
            client.close()
            continue

        if len(incoming.decode('utf-8').strip().split("\x00")) != 3:
            print_gui_with_log("{} didn't send a correctly formated message.".format(addr))
            client.sendall(struct.pack('?', False))
            client.close()
            continue

        success = False

        typ, name, pasw = incoming.decode('utf-8').strip().split("\x00")
        pasw = hashlib.sha256(pasw.encode('utf-8')).hexdigest()

        mess = ""

        if typ.startswith("c"):
            mess = "create an account"
            if addUser(name, pasw):
                success = True
                client.sendall(struct.pack('?', True))
            else:
                client.sendall(struct.pack('?', False))
        elif typ.startswith("l"):
            mess = "login to an account"
            if checkLogin(name, pasw):
                success = True
                client.sendall(struct.pack('?', True))
            else:
                client.sendall(struct.pack('?', False))
        else:
            print_gui_with_log("{} tried to send invalid command: {}".format(addr, incoming))
            mess = 0

        if mess != 0:
            print_gui_with_log('{} tried to {} with {} and {} at {}'.format(addr, mess, name, pasw, datetime.datetime.today().replace(microsecond=0).replace(":", ";")))
            print_gui_with_log('Result of login: {}'.format(success))

        client.close()

serverSocket.close()

print_gui_with_log(" ")
print_gui_with_log("Server closed: {}".format(datetime.datetime.now()))

print_gui_with_log("Attempting logfile reload thread closedown")
runningLogFileThread = False
while reloadLogfileThreadOpen:
    time.sleep(0.1)
print_gui_with_log("Logfile reload thread stopped")

print_gui_with_log("Attempting to close logfile, assume success.")
log_file.close()
