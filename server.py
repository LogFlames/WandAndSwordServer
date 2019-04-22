# -*- coding: utf-8 -*-

import socket
import threading
import queue
import time
import struct

from ClientClass import *
from GameClass import *

try:
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    print("Failed to create initial socket. Exiting")
    exit()

def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
    except:
        print('    No internet connection.')
        print('    Try reconnection and restarting the server')
        print("    Launching into default host: 'localhost'")
        return 'localhost'

    return s.getsockname()[0]

runningInputThread = True
threadOpen = False

def read_kbd_input(inputQueue):
    global threadOpen

    print('    Terminal ready for keyboard input')
    threadOpen = True
    inputQueue.put('help')
    while runningInputThread:
        input_str = input()
        inputQueue.put(input_str)
    threadOpen = False

hostChosen = False
while not hostChosen:
    host = input("Use host-machine ip or localhost? (ip <---> localhost): ")
    if host == "ip":
        host = getIP()
        print('    Host ip set to: {}'.format(str(host)))
        hostChosen = True
    elif host == 'localhost':
        print('    Host is hosted only on local machine')
        hostChosen = True
    else:
        print("    Option '{}' isn't known by the program, please try again.".format(host))

"""
portChosen = False
while not portChosen:
    port_str = input('What port should the program launch into?: ')
    try:
        port = int(port_str)
    except:
        print("    The input given couldn't be converted into a number, please only type whole numeric values.")
        continue
    try:
        serverSocket.bind((host, port))
        print('        Server is running on --> {}:{}'.format(host, port))
        portChosen = True
    except:
        print('    Port {} is already in use on the host machine'.format(port))
"""

try:
    serverSocket.bind((host, 8059))
    print(' ')
    print('        Server is running on --> {}:{}'.format(host, '8059'))
    print(' ')
except:
    print('    Port {} is already in use on the host machine, free the port and try again.'.format('8059'))

bufferOrMsg = 'none'
while bufferOrMsg == 'none':
    bufOrMsgInput = input('Should the program forward buffers or convert them into messages? (buf (standard) <---> msg): ')
    if bufOrMsgInput == 'buf':
        bufferOrMsg = 'buf'
    elif bufOrMsgInput == 'msg':
        bufferOrMsg = 'msg'
    else:
        print("    Option '{}' isn't known by the program, please try again".format(bufOrMsgInput))

game = GameClass(bufferOrMsg)
clientID = 0

serverSocket.listen(5)
serverSocket.setblocking(0)
serverSocket.settimeout(0.03)

running = True

inputQueue = queue.Queue()

print('    Starting input thread')
inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=True)
inputThread.start()
print('    Input thread started')

print('    Starting main server loop')
print(' ')
while running:
    if inputQueue.qsize() > 0:
        line = inputQueue.get().strip()
        if line == 'help' or line == '?':
            print('Help menu:')
            print('help - Show this menu')
            print('exit - close the server')
            print('kick-all - Kicks all clients from server')
            print('list-clients - Lists all clients connected to the server')
            print(' ')
        elif line == 'exit':
            print('Attempting to close the server')
            running = False
        elif line == 'kick-all':
            for client in game.clients:
                client.clientSocket.close()
                client.toBeRemoved = True
            print('Kicked all clients from server')
            print(' ')
        elif line == 'list-clients':
            print('Clients: ')
            for client in game.clients:
                print(client.addr)
            print(' ')
        else:
            print('{} is a unknown command, type help for a list of commands.'.format(line))

    try:
        s, addr = serverSocket.accept()
    except:
        s = False

    if s:
        clientID += 1
        game.addClient(ClientClass(clientID, s, addr))

        s.setblocking(0)
        s.settimeout(0.03)

        print('Incomming connection from {}'.format(addr))

    game.recvData()

    game.cleanClients()

    game.sendData()

print('        Attempting to close down serversocket')
serverSocket.close()
print('        Serversocket closed')
print('        Closing down input thread')
runningInputThread = False
print('    Press ENTER to ensure safe closedown of input thread...')
while threadOpen:
    time.sleep(0.5)
print('        Thread closed properly')
print('        Server closed down properly')
