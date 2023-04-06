import requests
import subprocess
import re
import threading
import socket
from time import sleep

BACKEND_URL = 'http://localhost:8000/v1/api/relay' # https://example.com/
ALLOWED_DRONES = ['60-60-1f-5b-4b-ea', '60-60-1f-5b-4b-d8', '60-60-1f-5b-4b-78']

class Relaybox:
    def __init__(self, name, password) -> None:
        self.name = name
        self.password = password
        self.drones = {}
        self.token = None
    
    def connect_to_backend(self) -> None:
        try:
            query = { 'name': self.name, 'password': self.password }
            response = requests.post(f'{BACKEND_URL}/handshake', json=query)
            if response.status_code != 200: # Every HTTPException.
                print(f"An error occured while trying to connect to URL [{response.url}] with status code {response.status_code}")
                sleep(2)
                print(f"Trying again...")
                self.connect_to_backend()

            token = response.json().get('access_token')
            self.token = token
            print("(!) Connected to backend")
        except Exception:
            print(f"Error trying to connect to backend")


    def post_drones_to_backend(self) -> None:
        ...
    
    def scan_for_drone(self, callback) -> None: # THREAD!
        while True:
            regex = r"""(192\.168\.137\.[0-9]{0,3}) *([0-9a-z-]*)""" #-Bjørn
            output = str(subprocess.check_output(['arp', '-a']))
            output = output.replace(" \r","")
            scanned_drones = re.findall(regex, output) # [(192.168.137.xxx, 00:00:00:00:00:00), ...] 

            for drone in scanned_drones[:]:
                if drone[1] not in ALLOWED_DRONES:
                    scanned_drones.remove(drone)
            
            for drone in scanned_drones[:]:
                cmd = f"ping -w 100 -n 2 {drone[0]}" 
                pinging = str(subprocess.run(cmd, capture_output=True))
                pinging = pinging.replace(" \r","")

                if "Received = 0" in pinging:
                    scanned_drones.remove(drone)

            print(scanned_drones)
            callback(scanned_drones)
    
    def filter_scanned_drones(self, scanned_drones):
        # Check for connected drone
        for drone in scanned_drones:
            ips_mapped = []
            for name in self.drones:
                ips_mapped.append(self.drones[name].get('Ip'))

            if drone[0] not in ips_mapped:
                print(f"[CONNECTED] {drone}")
                self.add_drone(drone[0])
        
        # Check for disconnected drone
        drones_object_list = []
        for name in self.drones:
            drones_object_list.append(self.drones[name].get('objectId'))

        for drone in drones_object_list:
            ips_mapped = []
            for x in scanned_drones:
                ips_mapped.append(x[0])
            
            if drone.host not in ips_mapped:
                print(f"[DISCONNECTED] {drone.name} {drone.host}")
                self.delete_drone(drone.name)
                self.disconnected_drone(drone)


    def add_drone(self, host) -> None:
        # find a unique name for the drone
        used_names = []
        for drone in self.drones.keys():
            used_names.append(drone)
        
        for num in range(1, 255):
            if "drone_{:03d}".format(num) not in used_names:
                drone_name = "drone_{:03d}".format(num)
                break

        # create a class for the drone now
        drone = Drone(name=drone_name, parent=self.name, host=host)
        self.drones[drone_name] = { "Ip": host, "objectId": drone }

        drone_thread = threading.Thread(target=drone.start, args=())
        drone_thread.start()



    def delete_drone(self, name) -> None:
        object = self.drones[name].get('objectId')
        del object
        self.drones.pop(name)
    
    def heartbeat(self, callback) -> None:
        print("Started heartbeat...")
        scan_for_drone_thread = threading.Thread(target=self.scan_for_drone, args=(callback,))
        scan_for_drone_thread.run()

    def disconnected_drone(self, drone: object) -> None:
        query = { 'name': drone.name, 'parent': drone.parent }
        response = requests.post(f'{BACKEND_URL}/drone/disconnected', json=query)
        if response.status_code != 200: # Every HTTPException
            print(f"Error: [{response.url}] with status code {response.status_code}")
            print(f"Trying again...")
            self.disconnected_drone(drone)
    
        

class Drone:
    def __init__(self, name, parent, host) -> None:
        self.name = name
        self.parent = parent
        self.host = host
        self.video_port = None #NOTE: video_port for relay -> backend

    
    def start(self):
        print(f"Starting {self.name}")
        self.get_ports()
        self.set_drone_video_port()


    def get_ports(self):
        query = { 'name': self.name, 'parent': self.parent }
        response = requests.get(f'{BACKEND_URL}/new_drone', json=query)
        
        if response.status_code != 200: # Every HTTPException
            print(f"Error trying to get available port from URL [{response.url}] with status code {response.status_code}")
            print(f"Trying again...")
            self.get_ports()
        
        port = response.json().get('video_port')
        print(f"[RES] Received port {port} for {self.name} on [{self.parent}]")
        self.video_port = port

    def set_drone_video_port(self):
        drone_video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        drone_video_socket.bind(('0.0.0.0', self.video_port))

        # initialize SDK mode
        command_set = self.send_control_command(drone_video_socket, "command", self.host, 8889, 2048)
        print(command_set)

        set_ports = self.send_control_command(drone_video_socket, f"port 8889 {self.video_port}", self.host, 8889, 2048)
        print(set_ports)

        stream_on = self.send_control_command(drone_video_socket, "streamon", self.host, 8889, 2048)
        print(stream_on)

        while True:
            feed = drone_video_socket.recvfrom(2048)
            print(feed, "port", self.video_port)
            sleep(3)
        

    def send_control_command(self, socket: object, command: str, ip: str, port: int, buffer_size: int) -> str:
        socket.sendto(bytes(command, 'utf-8'), (ip, port))
        drone_response = socket.recvfrom(buffer_size)
        return drone_response







if __name__ == '__main__':
    relay = Relaybox("relay_0001", "123")
    relay.connect_to_backend()
    relay.heartbeat(relay.filter_scanned_drones)