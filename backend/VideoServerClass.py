import sys, time
import threading
import socket
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

class video_server:
    def __init__(self, UDP_port):
        self.UDP_port = UDP_port
        self.drone_on = True
        start_thread = threading.Thread(target=self.start, args=())
        start_thread.start()

    def start(self):
        self.local_host = '' #LocalHost depending on which device runs the server
        self.connections = []

        #Define UDP Address and Socket
        self.local_udp_addr = (self.local_host, self.UDP_port) #UDP Address
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Socket for stream
        self.udp_sock.bind(self.local_udp_addr) #Bind the udp socket to the UDP Address
        print(f'Server Address: {self.local_udp_addr}')

        self.check_conn()

    def handle_stream(self):
        #Send confirmation Packets
        for conn in self.connections:
            self.udp_sock.sendto("poop".encode('utf-8'), conn)

        while len(self.connections) == 2 and self.drone_on == True: #While both 
            try:
                data, relay = self.udp_sock.recvfrom(2048)

            except Exception:
                print(f'Could not retrieve message: Socket Most Likely Closed.')
                return
            
            try:
                for conn in self.connections:
                    if conn != relay:
                        try:
                            self.udp_sock.sendto(data, conn)
                        except:
                            print("Could not send data to client. Client most likely disconnected.")
                            self.connections.remove(conn)

            except Exception as c:
                print(f"Could not check connections: {c}")
                return
        
        print("Connection closed")
        if self.drone_on == True:
            print("Client has disconnected from session")
        return
                

    def check_conn(self):
        address = None
        while len(self.connections) < 2 and self.drone_on == True: #Wait for both user and relaybox
            if self.drone_on == True:
                try:
                    data, address = self.udp_sock.recvfrom(2048)
                except Exception as e:
                    print('Listen or Send Cancelled: Socket Most Likely Closed.')

            if address != None:
                if address not in self.connections: #If the connection is not in the list
                    self.connections.append(address)
                    print(f"Connections: {self.connections}")

            if self.drone_on == True and len(self.connections) == 2:
                print("Both have connected via udp")
                self.handle_stream()

            else:
                if self.drone_on == False:
                    print("Error checking connections, failed.")
                    break

                print("Waiting for Client")
        


'''
.
# Create a Server instance which handles the video connection
    udp_object = video_server(UDP_port = port)
    stream_thread = threading.Thread(target=udp_object.start(), args=())
    stream_thread.start()


class threaded_TCP_server:
    def __init__(self, tcpPort, udpPort):
        self.local_host = '' #LocalHost Depending on which device runs the server
        self.client_connected = False
        print(f'Server Addres: {socket.gethostbyname(socket.gethostname())}')

        self.tcp_connections = []

        #self.local_tcp_addr = (self.local_host, tcpPort) #TCP Address
        self.local_udp_addr = (self.local_host, udpPort) #UDP Address

        #self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket for Commands
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Socket for stream

        #self.tcp_sock.bind(self.local_tcp_addr) #Bind the tcp socket to the TCP address
        self.udp_sock.bind(self.local_udp_addr) #Bind the udp socket to the UDP Address

        #Run threads for each connection
        #tcp_Thread = threading.Thread(target=self.tcp, args=(self.tcp_sock)) #The client function is also the one to accept both connections
        #tcp_Thread.start()

        udp_Thread = threading.Thread(target=self.udp, args=(self.udp_sock)) 
        udp_Thread.start()




    def udp(self, socket):
        while True:
            try:
                streamdata = socket.recvfrom(2048)
                #socket.sendto(streamdata) #Missing target, send to client ip and port
            except Exception as e:
                print(f"Could not retreive Video stream: {e}")


    def server_loop(self):
        while True:
            print('<Server> Ready for new client')
            connection_socket, source_ip = self.sock.accept()
            thread = threading.Thread(target=self.thread, args=(connection_socket, source_ip), daemon=True)

            thread.start()


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
    '''