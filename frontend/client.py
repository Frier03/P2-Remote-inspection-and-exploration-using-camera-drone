#Libraries
import requests
import threading
import socket
import time, copy
import numpy as np
import cv2

BACKEND_URL = 'http://localhost:8000/v1/api/frontend'

class Client:
    def __init__(self) -> None:
        #-----# Local Variables #-----#
        self.token = None #Token from backend

        #-----# Session Variables #-----#
        self.session = requests.Session()

        #-----# Server Information #-----#
        self.server_info = None
        self.active_relays = []
        self.active_dict = {}

        self.login()

    def login(self):
        #Get login information
        self.username = input("Username: ")
        self.password = input("Password: ")

        try:
            #Send login request
            query = {'name': self.username, 'password': self.password}
            response = requests.post(f'{BACKEND_URL}/login', json=query)

            if response.status_code != 200: #Every HTTPException.
                if not response.json().get('access_token'):
                    print(f"Incorrect Username or Password: {response.status_code}")
                else:
                    print(f"Server is offline | Could not connect")

            #Token information
            self.token = response.json().get('access_token')
        
        except Exception:
            print("Failed Connecting to Backend")
            self.login()

        self.start()
        

    def start(self):
        #Open Thread that keeps getting info from backend
        self.info_trigger = threading.Event()
        info_thread = threading.Thread(name='grab_info', target=self.get_info, args=())
        info_thread.start()
        self.info_trigger.set()

        #Go to Drone choice
        self.drone_choice()


    def logout(self):
        pass

    def get_info(self):
        while True:
            self.info_trigger.wait()

            # Retrieve information from backend
            try:
                response = requests.get(f'{BACKEND_URL}/relayboxes/all')
                info: dict = response.json()
                self.server_info = info
            except Exception as e:
                print(f"{e}: Could not retrieve Relay and Drone Data")

            # Sort and append information
            temp_dict = {}
            active_relays = []
            for relay in info.keys(): #Relay is outer library and drone is inner library
                active_relays.append(relay)

                #For Active Drone Display
                active_drones = []
                for drone in info[relay]:
                    active_drones.append(drone)

                temp_dict[relay] = active_drones


            #Update the global access list
            if self.active_relays != active_relays:
                self.active_relays = copy.deepcopy(active_relays)
            
            if self.active_dict != temp_dict:
                self.active_dict = copy.deepcopy(temp_dict)

            self.info_trigger.clear()

    def drone_choice(self):
        self.info_trigger.set() #Update the library and list containing information
        while True:
            if self.server_info != None:
                # Print Options
                n = 0
                for relay in self.active_dict.keys():
                    print(f"{relay}:\n")
                    for i in range(len(self.active_dict[relay])):
                        print(f"{n}.{i}: {self.active_dict[relay]}\n")
                    n += 1
            
            try:
                id = str(input("('u' to manually update) Drone ID: "))

                if id.lower() == "u":
                    self.info_trigger.set()
                else:
                    id = id.split(".")
                    relay = self.active_relays[int(id[0])]
                    drone = self.active_dict[relay][int(id[1])]
                    udp_port = self.server_info[relay][drone]['ports']

                    # Start Drone Connection
                    session = drone_session(port=udp_port) #Can be done as a thread
            
            except Exception as e:
                print(f"Error: {e}")



#----------# Creates a Drone Session When Port and Drone has been Chosen #----------#

class drone_session:
    def __init__(self, port) -> None:
        print(f"Entered session on port {port}")
        self.udpport = port
        self.backend_address = ('127.0.0.1', self.udpport)
        self.host = ''

        #Create Socket
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Socket for stream
        self.udp_sock.bind((self.host, 3000))

        #Start activation
        self.verify()

    def verify(self):
        while True:
            # Send verification Packet
            try:
                print("Sending Verification Packet")
                self.udp_sock.sendto("poop".encode('utf-8'), self.backend_address)
                break
            except Exception as e:
                print(f"Could not send verification message: {e}")
        
        # Start Thread
        self.video_thread = threading.Thread(target=self.video_stream)
        self.video_thread.start()
        self.video_thread.join()

        while True:
            pass
    
    def video_stream(self):
        print("Entered Video Capture")

        packet_data = b""
        while True:
            try:
                # Receive the encoded frame
                encoded_frame, addr = self.udp_sock.recvfrom(2048)
                packet_data += encoded_frame

                #End of frame
                if len(encoded_frame) != 1460:
                    print(f"Decoding, packet length: {len(encoded_frame)}, accumulated data length: {len(packet_data)}")

                    # Decode the encoded frame
                    frame = np.frombuffer(packet_data, dtype=np.uint8)
                    decoded_frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                    
                    if decoded_frame is not None:
                        print(f"Not None, decoded frame shape: {decoded_frame.shape}")
                        # Display the decoded frame
                        cv2.imshow('Live Stream', decoded_frame)

                        # Exit the loop if 'q' is pressed
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    else:
                        print("Decoded frame is None")

                    packet_data = b""


            except Exception as e:
                print(f"Video Error: {e}")
                break
        
        cv2.destroyAllWindows()
        self.udp_sock.close()

if __name__ == "__main__":
    object = Client()