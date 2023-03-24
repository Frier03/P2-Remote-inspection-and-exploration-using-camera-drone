import socket, time
import threading
from ServerClass import threaded_TCP_server

#Constantly Listen for Connections and initate class when
ServerIP = ''
ListenPort = 5000
ListenAddr = (ServerIP, ListenPort)
Connectport = 5000
ENCODING = 'utf-8'

#Open Listen Socket for the server
ListenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ListenSocket.bind(ListenAddr) #Bind the Socket to the listen address
ListenSocket.listen()

def handshake(Conn, Addr, Connectport):
    try:
        data, addr = Conn.recv(1024) #Receive Key from relaybox
    except Exception as e:
        print(f"Could not retrieve key: {e}")


    key = data.decode(ENCODING)
    print(key)

    #HAND SHAKE AUTHENTICATION
    authenticated = False
    with open("/whitelist.txt", 'r') as auth:
        for line in auth:
            if line.strip() == key:
                print("Authenticated")
                authenticated = True
                auth.close()
    
    if authenticated == False:
        print("Authentication Failed! Closing Connection...")
        auth.close() #Close the file
        Conn.close() #Close the connection to the relaybox
        return Connectport#End auth if auth key is not true

    tcpPort = Connectport + 1
    udpPort = Connectport + 2
    Connectport += 2

    threading.Thread(target=ServerInstance, args=(tcpPort, udpPort)).start()
    time.sleep(1) #Give the Server Time to start

    try:
        Conn.sendall(f'{tcpPort}, {udpPort}'.encode(ENCODING))
    except Exception as e:
        print(f'Message Could not be sent: {e}')


def ServerInstance(tcpPort, udpPort):
    server = threaded_TCP_server(tcpPort, udpPort) #Create the server instance for the handled relaybox


print('Listening for Incoming Connections')
while True: #Constantly Listen for Connections
    Conn, Addr = ListenSocket.accept()

    #When connection has been accepted
    Connectport = handshake(Conn=Conn, Addr=Addr, Connectport=Connectport)