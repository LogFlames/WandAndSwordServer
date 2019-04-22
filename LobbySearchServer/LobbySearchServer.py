import socket

lobby_list = []
host = ""
port = 8061

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def getIP():
    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        ss.connect(('8.8.8.8', 80))
    except:
        print('    No internet connection.')
        print('    Try reconnection and restarting the server')
        print("    Launching into default host: 'localhost'")
        return 'localhost'

    return ss.getsockname()[0]

host = getIP()
s.bind((host,port))

while True:
    data, addr = s.recvfrom(1024)
    
    if data != 0:
        print("New lobby: " + addr)
        lobby_list.append(addr)
    else:
        s.sendto(lobby_list, (addr, 8059))