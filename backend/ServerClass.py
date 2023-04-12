import sys, time
import threading
import socket

class threaded_TCP_server:
    def __init__(self, tcpPort, udpPort):
        self.local_host = '' #LocalHost Depending on which device runs the server
        self.client_connected = False
        print(f'Server Addres: {socket.gethostbyname(socket.gethostname())}')

        self.tcp_connections = []

        self.local_tcp_addr = (self.local_host, tcpPort) #TCP Address
        self.local_udp_addr = (self.local_host, udpPort) #UDP Address

        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket for Commands
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Socket for stream

        self.tcp_sock.bind(self.local_tcp_addr) #Bind the tcp socket to the TCP address
        self.udp_sock.bind(self.local_udp_addr) #Bind the udp socket to the UDP Address

        #Run threads for each connection
        tcp_Thread = threading.Thread(target=self.tcp, args=(self.tcp_sock)) #The client function is also the one to accept both connections
        tcp_Thread.start()

        udp_Thread = threading.Thread(target=self.udp, args=(self.udp_sock)) 
        udp_Thread.start()


    def tcp(self, socket):
        relay = False #Check if the relay box has connected.
        socket.listen(2) #Await connection from client and from relaybox

        while True:
            conn, addr = socket.accept() #Accept Connections from relay and client
            self.tcp_connections.append(conn)

            while relay == True: #Only start to handle client if relaybox has connected (Relay box will connect before client)
                #Retreive the data from the client
                try:
                    data, addr = conn.recv(128) #Receive data from client
                except Exception as e:
                    print(f"Could not retreive commands: {e}")

                try:
                    self.tcp_connections[0].send(data)
                except Exception as e:
                    print(f"Could not send data to relaybox: {e}")

            if relay == False: #Check flag: Has the relay box connected first?
                relay = True

    def udp(self, socket):
        while True:
            try:
                streamdata = socket.recvfrom(2048)
                #socket.sendto(streamdata) #Missing target, send to client ip and port
            except Exception as e:
                print(f"Could not retreive Video stream: {e}")


    '''
    def server_loop(self):
        while True:
            print('<Server> Ready for new client')
            connection_socket, source_ip = self.sock.accept()
            thread = threading.Thread(target=self.thread, args=(connection_socket, source_ip), daemon=True)

            thread.start()
    '''