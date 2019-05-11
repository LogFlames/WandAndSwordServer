# -*- coding: utf-8 -*-

import socket
import threading
import queue
import time
import struct
import re
import datetime
import os

from ClientClass import ClientClass
from GameClass import GameClass

LOG_FILES = "LOGS"

path_to_script = os.path.dirname(__file__)
path_to_logs = os.path.join(path_to_script, LOG_FILES)

os.makedirs(path_to_logs, exist_ok=True)

session_temp = str(int(time.time()))

SESSION_ID = hex(int(session_temp[len(session_temp) - 10:]))

log_file = open(os.path.join(path_to_logs, "Log-gameplay-server-{}-{}.txt".format(SESSION_ID, str(datetime.datetime.today().replace(microsecond=0)).replace(":", ";"))), "a")

def print_log(msg):
    print(msg)
    log_file.write(msg + "\n")

try:
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print_log("Failed to create initial socket. Exiting")
    log_file.close()
    exit()

def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
    except:
        print_log('    No internet connection.')
        print_log('    Try reconnection and restarting the server')
        print_log("    Launching into default host: 'localhost'")
        return 'localhost'

    return s.getsockname()[0]

runningInputThread = True
threadOpen = False

def read_kbd_input(inputQueue):
    global threadOpen

    print_log('    Terminal ready for keyboard input')
    threadOpen = True
    inputQueue.put('help')
    while runningInputThread:
        input_str = input()
        inputQueue.put(input_str)
    threadOpen = False

runningLogFileThread = True

def reload_log_file(timeInterval):
    global log_file

    print_log('    Logfile will reload every {} seconds'.format(str(timeInterval)))

    while runningLogFileThread:
        waitedTime = 0
        while waitedTime < timeInterval:
            waitedTime += 0.5
            if not runningLogFileThread:
                return
            time.sleep(0.5)

        if runningLogFileThread:
            print_log('Reloading logfile...')

            log_file.close()
            log_file = open(os.path.join(path_to_logs, "Log-gameplay-server-{}-{}.txt".format(SESSION_ID, str(datetime.datetime.today().replace(microsecond=0)).replace(":", ";"))), "a")

            print_log('New logfile started...')

hostChosen = False
while not hostChosen:
    host = input("Use host-machine ip or localhost? (ip <---> localhost): ")
    if host == "ip" or host == 'i':
        host = getIP()
        print_log('    Host ip set to: {}'.format(str(host)))
        hostChosen = True
    elif host == 'localhost' or host == 'l':
        host = 'localhost'
        print_log('    Host is hosted only on local machine')
        hostChosen = True
    else:
        print_log("    Option '{}' isn't known by the program, please try again.".format(host))

"""
portChosen = False
while not portChosen:
    port_str = input('What port should the program launch into?: ')
    try:
        port = int(port_str)
    except:
        print_log("    The input given couldn't be converted into a number, please only type whole numeric values.")
        continue
    try:
        serverSocket.bind((host, port))
        
        print_log('        Server is running on --> {}:{}'.format(host, port))
        portChosen = True
    except:
        print_log('    Port {} is already in use on the host machine'.format(port))
"""

try:
    serverSocket.bind((host, 8059))
    print_log(' ')
    print_log('        Server is running on --> {}:{}'.format(host, '8059'))
    print_log(' ')
except:
    print_log('    Port {} is already in use on the host machine, free the port and try again.'.format('8059'))

playerCap = 2
while playerCap == -1:
    playerCap_str = input('How many players should be able to join? (-1 == no limit): ')
    try:
        playerCap = int(playerCap_str)
        if playerCap == -1:
            break
    except:
        print_log("{} isn't a whole numeric value".format(playerCap_str))

game = GameClass()
clientID = 0

serverSocket.listen(5)
serverSocket.setblocking(0)
serverSocket.settimeout(0.001)

debug = False

running = True

inputQueue = queue.Queue()

print_log('    Debug is currently set to DISABLED')

print_log('    Starting input thread')
inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=True)
inputThread.start()
print_log('    Input thread started')

print_log('    Starting logfile reload thread')
reloadLogThread = threading.Thread(target=reload_log_file, args=(7200,), daemon=True)
reloadLogThread.start()
print_log('    Logfile reload thread started')

print_log('    Starting main server loop')
print_log(' ')
while running:
    if inputQueue.qsize() > 0:
        line = inputQueue.get().strip()
        print_log(">>> " + line)
        if line == 'help' or line == '?':
            print_log('Help menu:')
            print_log('help - Show this menu')
            print_log('exit - close the server')
            print_log('kick-all - Kicks all clients from server')
            print_log('kick-(id)(id)(id)(...) - Kick client of specified id. example "kick-(3)", "kick-(5)(7)"')
            print_log('list-clients - Lists all clients connected to the server')
            print_log('resend-names - Resends all names to connected clients')
            print_log('debug - enable/disable debug mode.')
            print_log(' ')
        elif line == 'exit':
            print_log('Attempting to close the server')
            running = False
        elif line == 'kick-all':
            for client in game.clients:
                client.clientSocket.close()
                client.toBeRemoved = True
            print_log('Kicked all clients from server')
            print_log(' ')
        elif line.startswith('kick-('):
            ctkID = re.findall('\d+', line)
            ctkID = list(map(int, ctkID))
            if game.kick_clients(ctkID):
                print_log('Kicked requested clients')
            else:
                print_log("Couldn't find any clients with the requested IDs.")
        elif line == 'list-clients':
            print_log('Clients: ')
            for client in game.clients:
                print_log('ID: {}, Addr: {}, Name: {}'.format(client.clientID, client.addr, client.name))
            print_log(' ')
        elif line == 'resend-names':
            game.resendNames()
            print_log('Resent all name data to clients')
            for client in game.clients:
                print_log('ID: {}, Addr: {} ||| Name: {}'.format(client.clientID, client.addr, client.name))
            print_log(' ')
        elif line == 'debug':
            debug = not debug
            game.debug = debug
            game.update_clients_debug()
            if debug:
                status = "ENABLED"
            else:
                status = "DISABLED"

            print_log('Debug is {}'.format(status))
        else:
            print_log('{} is a unknown command, type help for a list of commands.'.format(line))

    try:
        s, addr = serverSocket.accept()
    except:
        s = False

    if s:
        if playerCap != -1 and len(game.clients) >= playerCap:
            print_log('Kicked {} from the server, already {}/{} players online'.format(addr, str(playerCap), str(playerCap)))
            s.close()
        else:
            clientID += 1
            game.addClient(ClientClass(clientID, s, addr, debug))

            s.setblocking(0)
            s.settimeout(0.001)

            print_log('Incoming connection from {}'.format(addr))

    game.update_print_request()

    for msg in game.prints:
        print_log(msg)
    game.prints = []

    game.recvData()

    game.cleanClients()

    game.sendData()

print_log('        Attempting to close down serversocket')
serverSocket.close()
print_log('        Serversocket closed')
print_log(' ')
print_log('        Closing down input thread')
runningInputThread = False
print_log('    Press ENTER to ensure safe closedown of input thread...')
while threadOpen:
    time.sleep(0.5)
print_log('        Thread closed properly')

print_log(' ')
print_log('    Attempting to close down log file, assume success')
runningLogFileThread = False
log_file.close()
print('    Logfile closed down properly')

print(' ')
print('    Server closed down properly')
