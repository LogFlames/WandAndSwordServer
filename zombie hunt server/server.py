# -*- coding: utf-8 -*-
import socket
import threading
import queue
import struct
import datetime
import urllib.request
import time

from clientClass import ClientClass
class ServerClass:
    def __init__(self):
        # Set variables
        self.inputQueue = queue.Queue()
        self.client_ips = []
        self.client_sockets = []
        self.host = ""
        self.clientcount = 0
        self.ipv4 = ""
        self.ipv6 = ""
        self.tcp_port = 55555
        self.udp_port = 55554

        help_menu = '''
            *** HELP MENU ***
            help - shows this help menu
            exit - close server
            list-clients - shows list of all connected clients
            server-info - shows server; ip, ports...
            '''

        # Setup server
        try:
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverSocketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            serverSocket.listen(5)
            serverSocket.setblocking(0)
            serverSocket.settimeout(0.2)
            serverSocket.bind((self.host,self.tcp_port))

            serverSocketUDP.setblocking(0)
            serverSocketUDP.settimeout(0.001)
            serverSocket.bind((self.host,self.udp_port))
        except socket.error as err:
            print("Error when setting up server sockets...")
            print(err)
            exit()

        try:
            self.ipv4 = urllib.request.urlopen("https://ipv4bot.whatismyipaddress.com/").read().decode("utf8")
            self.ipv6 = socket.gethostbyname_ex(self.host)[2][2]
        except:
            print("Could not fetch server ips...")

        # On script close def
        def __exit__():
            # Close the server sockets
            serverSocket.close()
            serverSocketUDP.close()

        # Create variables for the accept clients def
        global runningAcceptClientThread
        global acceptClientsThreadOpen
        runningAcceptThreadOpen = True
        runningAcceptClientThread = True

        def accept_clients(clinetcount):
            global acceptClientsThreadOpen
            acceptClientsQue = queue.Queue()
            acceptClientsThreadOpen = True
            clientID = 0
            
            while runningAcceptThreadOpen:
                try:
                    print("Tried listening for client connectection " + time.time())
                    clientSocket, addr = serverSocket.accept()
                except:
                    pass
                else:
                    clientID += 1
                    acceptClientsQue.put(ClientClass(clientID, clientSocket, addr))
                    print("Incoming connection from {}:{}".format(addr[0],addr[1]) + " " + time.time()) # Print the clients ip and port
                    clinetcount += 1

        # variables for read_kbd_input def
        self.running = True
        self.runningInputThread = True
        self.inputThreadOpen = False

        def read_kbd_input(inputQueue):
            global inputThreadOpen

            print("Terminal ready for keyboard input...")
            inputThreadOpen = True
            inputQueue.put("help")
            while self.runningInputThread:
                input_str = input(">>> ")
                inputQueue.put(input_str)
            inputThreadOpen = False

        # Print thread startup data
        print("Starting input thread...")
        inputThread = threading.Thread(target=(read_kbd_input), args=(self.inputQueue,), daemon=True)
        inputThread.start()
        print("Input thread started...")

        print("Starting client accept thread...")
        acceptClientsThread = threading.Thread(target=(accept_clients), args=(self.clientcount,), daemon=(True))
        acceptClientsThread.start()
        print("Client accept thread started...")

        print("Starting main server loop...")

        # Main loop input
        while self.running:
            if self.inputQueue.qsize() > 0:
                self.line = self.inputQueue.get().strip()
                print(">>> {}".format(self.line))
                if self.line == "help" or self.line == "?":
                    print(help_menu)
                elif self.line == "list-clients":
                    print(*self.client_ips, sep="\n")
                elif self.line == "server-info":
                    print("\nIPV4: {}\nIPV:6: {}\nHOSTNAME: {}\nCLINET COUTN: {}\nPORT TCP: {}\nPORT UDP: {}\n".format(self.ipv4,self.ipv6,socket.gethostname(),self.clientcount,self.tcp_port,self.udp_port))
                else:
                    print("Command not recognized (" + str(self.line) +")") 

# Start the ServerClass
server = ServerClass()