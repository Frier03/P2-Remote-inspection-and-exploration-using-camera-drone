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
                    print("Drone Disconnected, Video Session Closed.")
                    break

                # print("Waiting for Client")