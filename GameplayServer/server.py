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

# Setup logfile

LOG_FILES = "LOGS"

path_to_script = os.path.dirname(__file__)
path_to_logs = os.path.join(path_to_script, LOG_FILES)

os.makedirs(path_to_logs, exist_ok=True)

session_temp = str(int(time.time()))

SESSION_ID = session_temp[len(session_temp) - 10:]

log_file = open(os.path.join(path_to_logs, "Log-gp-{}-{}.txt".format(SESSION_ID, str(datetime.datetime.today().replace(microsecond=0)).replace(":", ";"))), "a")

def print_log(msg):
    print(msg)
    log_file.write(msg + "\n")

runningLogFileThread = True
LogfileThreadOpen = False

def reload_log_file(timeInterval):
    global log_file
    global LogfileThreadOpen

    LogfileThreadOpen = True

    print_log('    Logfile will reload every {} seconds'.format(str(timeInterval)))

    while runningLogFileThread:
        waitedTime = 0
        while waitedTime < timeInterval:
            waitedTime += 0.5
            if not runningLogFileThread:
                LogfileThreadOpen = False
                return
            time.sleep(0.5)

        if runningLogFileThread:
            print_log('Reloading logfile...')

            log_file.close()
            log_file = open(os.path.join(path_to_logs, "Log-gp-{}-{}.txt".format(SESSION_ID, str(datetime.datetime.today().replace(microsecond=0)).replace(":", ";"))), "a")

            print_log('New logfile started...')

    LogfileThreadOpen = False

# Setup serversockets

try:
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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

def send_buffer_to_client_UDP(client, buf, addNum):
    if client.UDPAddr == None:
        return False
    try:
        if addNum:
            buf = struct.pack("I", 4294967295) + buf  # 2**32-1     b'\xff\xff\xff\xff'
            
        serverSocketUDP.sendto(buf, client.UDPAddr)
        if debug:
            print_log('Sent {} to {} using UDP'.format(buf, client.UDPAddr))
    except:
        print_log('Failed to send {} to {} using UDP'.format(buf, client.UDPAddr))

inputQueue = queue.Queue()
runningInputThread = True
inputThreadOpen = False

def read_kbd_input(inputQueue):
    global inputThreadOpen

    print_log('    Terminal ready for keyboard input')
    inputThreadOpen = True
    inputQueue.put('help')
    while runningInputThread:
        input_str = input()
        inputQueue.put(input_str)
    inputThreadOpen = False

runningAcceptClientThread = True
acceptClientsThreadOpen = False
acceptClientsQueue = queue.Queue()

def accept_clients(playerCap, game):
    global acceptClientsThreadOpen

    acceptClientsThreadOpen = True

    clientID = 0
    print_log('    Accept clients thread started')

    while runningAcceptClientThread:
        try:
            clientSocket, addr = serverSocket.accept()
        except:
            pass
        else:
            clientID += 1
            acceptClientsQueue.put(ClientClass(clientID, clientSocket, addr, debug))
            print_log('Incoming connection from {}'.format(addr))

    acceptClientsThreadOpen = False

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

try:
    serverSocket.bind((host, 8059))
    serverSocketUDP.bind((host, 8058))
    print_log(' ')
    print_log('        Server is running on --> {}:{}'.format(host, '8059'))
    print_log('        UDP server is running on --> {}:{}'.format(host, '8058'))
    print_log(' ')
except:
    print_log('    Port {} or {} is already in use on the host machine, make sure both ports and try again.'.format('8059', '8058'))

# Won't run while loop when playerCap 2 is selected in code
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

serverSocket.listen(5)
serverSocket.setblocking(0)
serverSocket.settimeout(0.2)

serverSocketUDP.setblocking(0)
serverSocketUDP.settimeout(0.001)

debug = False

running = True

print_log('    Debug is currently set to DISABLED')

print_log('    Starting input thread')
inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=True)
inputThread.start()
print_log('    Input thread started')

print_log('    Starting logfile reload thread')
reloadLogThread = threading.Thread(target=reload_log_file, args=(7200,), daemon=True)
reloadLogThread.start()
print_log('    Logfile reload thread started')

print_log('    Starting client accept thread')
acceptClientsThread = threading.Thread(target=accept_clients, args=(playerCap, game,), daemon=True)
acceptClientsThread.start()
print_log('    Client accept thread started')

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
            print_log('resend-client-ids - Resends all clients IDs to clients')
            print_log('send-udp-testpacket-(id)(id)(id)(...) - Sends a testpacket in udp to a client with the specified id, example: "send-udp-testpacket-(3)(5)", "send-udp-testpacket-(7)"')
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
            game.resend_names()
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
        elif line == 'resend-client-ids':
            game.send_client_IDs()
            print_log('Resending all client IDs to clients')
        elif line.startswith('send-udp-testpacket-('):
            ctsdIDs = re.findall('\d+', line)
            ctsdIDs = list(map(int, ctsdIDs))
            for clientID in ctsdIDs:
                client = game.get_client_id(clientID)
                if not client:
                    print_log("Couldn't find client with id {}".format(clientID))
                else:
                    send_buffer_to_client_UDP(client.addr, struct.pack("II", 10, 123456), True)
            print_log('Sent testpacket data')
        else:
            print_log('{} is a unknown command, type help for a list of commands.'.format(line))

    if acceptClientsQueue.qsize() > 0:
        client = acceptClientsQueue.get()
        if playerCap != -1 and len(game.clients) >= playerCap:
            print_log('Kicked {} from the server, already {}/{} players online'.format(client.addr, str(playerCap), str(playerCap)))
            client.clientSocket.close()
        else:
            print_log('{} was accepted into the server'.format(client.addr))
            game.add_client(client)

            client.clientSocket.setblocking(0)
            client.clientSocket.settimeout(0.001)

    game.update_print_request()

    for msg in game.prints:
        print_log(msg)
    game.prints = []

    # Hadndle udp input
    gotData = True
    while gotData:
        try:
            data, addr = serverSocketUDP.recvfrom(1024)
            gotData = True
        except:
            pass
        else:
            game.handle_udp_data(data, addr)

    # Handle TCP input
    game.recv_data()

    # Remove unwanted clients from list
    game.clean_clients()

    # Send requested data to clients using TCP
    game.send_data()

    # Send requested data to clients using UDP
    for udpRequestSend in game.udpToSend:
        send_buffer_to_client_UDP(udpRequestSend[0], udpRequestSend[1], udpRequestSend[2])
    game.udpToSend = []

print_log('        Attempting to kick all clients from server')
for client in game.clients:
    client.clientSocket.close()
    client.toBeRemoved = True
game.clean_clients()

print_log('        Kicked all clients from server')

print_log('        Attempting to close client accept thread')
runningAcceptClientThread = False
while acceptClientsThreadOpen:
    time.sleep(0.1)
print_log('        Accept clients thread safetly closed down')

print_log('        Attempting to close down serversocket')
serverSocket.close()
print_log('        Serversocket closed')
print_log('        Closing down input thread')
runningInputThread = False
print_log('    Press ENTER to ensure safe closedown of input thread...')
while inputThreadOpen:
    time.sleep(0.1)
print_log('        Thread closed properly')

print_log('        Attempting to close logfile reload thread')
runningLogFileThread = False
while LogfileThreadOpen:
    time.sleep(0.1)
print_log('        Logfile reload thread safetly closed down')

print_log('        Attempting to close down log file, assume success')
log_file.close()
print('        Logfile closed down properly')

print(' ')
print('Server closed down properly')
