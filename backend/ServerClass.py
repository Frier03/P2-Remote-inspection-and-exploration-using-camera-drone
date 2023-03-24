import sys, time
import threading
import socket

class threaded_TCP_server:
    def __init__(self, tcpPort, udpPort):
        self.local_host = '' #LocalHost Depending on which device runs the server
        print(f'Server Addres: {socket.gethostbyname(socket.gethostname())}')

        self.local_tcp_addr = (self.local_host, tcpPort) #TCP Address
        self.local_udp_addr = (self.local_host, udpPort) #UDP Address

        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket for Commands
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Socket for stream

        self.tcp_sock.bind(self.local_tcp_addr) #Bind the tcp socket to the TCP address
        self.udp_sock.bind(self.local_udp_addr) #Bind the udp socket to the UDP Address

        #Run threads for each connection
        tcp_Thread = threading.Thread(target=self.tcp_client, args=(self.tcp_sock))
        tcp_Thread.start()

        udp_Thread = threading.Thread(target=self.udp, args=(self.udp_sock))
        udp_Thread.start()


    def tcp_client(self, socket):
        relay = False #Check if the relay box has connected.
        socket.listen(2) #Await connection from client and from relaybox

        while True:
            conn, addr = socket.accept() #Accept Connections from relay and client

            while relay == True: #Only start to handle client if relaybox has connected (Relay box will connect before client)
                pass #Handle client


            if relay == False: #Check if the relaybox has connected
                tcp_client_thread = threading.Thread(target=self.tcp_relay, args=(conn, addr))
                tcp_client_thread.start()
                relay = True
        
    
    def tcp_relay(self, conn, addr):

    def udp(self, socket):
        pass
       

    def server_loop(self):
        while True:
            print('<Server> Ready for new client')
            connection_socket, source_ip = self.sock.accept()
            thread = threading.Thread(target=self.thread, args=(connection_socket, source_ip), daemon=True)

            thread.start()