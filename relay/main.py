import requests
import subprocess
import re
import threading
from time import sleep

BACKEND_URL = 'http://localhost:8000' # https://example.com/

class Relaybox:
    def __init__(self, name, password) -> None:
        self.name = name
        self.password = password
        self.drones = {}
        self.token = None
    
    def connect_to_backend(self) -> None:
        response = requests.post(f'{BACKEND_URL}/v1/auth/relay/handshake', json={ 'name': self.name, 'password': self.password})
        token = response.json().get('access_token')
        self.token = token

    def post_drones_to_backend(self) -> None:
        
        ...
    
    def scan_for_drone(self, callback) -> None: # THREAD!
        while True:
            regex = r"""(192\.168\.137\.[0-9]{0,3}) *([0-9a-z-]*)""" #-Bjørn
            output = subprocess.check_output(['arp', '-a'])
            output = output.replace(" \r","")
            scanned_drones = re.findall(regex, output) # [(192.168.137.xxx, 00:00:00:00:00:00), ...] 
            callback(scanned_drones)
            sleep(0.5)
    
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

    def delete_drone(self, name) -> None:
        object = self.drones[name].get('objectId')
        del object
        self.drones.pop(name)
    
    def heartbeat(self, callback) -> None:
        scan_for_drone_thread = threading.Thread(target=scan_for_drone_thread, args=(callback,))
        scan_for_drone_thread.run()

class Drone:
    def __init__(self, name, parent, host) -> None:
        self.name = name
        self.parent = parent
        self.host = host

if __name__ == '__main__':
    relay = Relaybox("relay_0001", "123")
    #relay.connect_to_backend()
    #relay.heartbeat(relay.filter_scanned_drones)
    
    relay.drones = {}
    relay.filter_scanned_drones( [('192.168.137.200', '00:00:00:00:00')] ) #OK
    sleep(2)
    print("\n")
    relay.filter_scanned_drones( [('192.168.137.200', '00:00:00:00:00'), ('192.168.137.133', '00:00:00:00:00')] ) #OK
    sleep(2)
    relay.filter_scanned_drones( [('192.168.137.133', '00:00:00:00:00')] )
    sleep(2)
    relay.filter_scanned_drones( [('192.168.137.200', '00:00:00:00:00'), ('192.168.137.133', '00:00:00:00:00')] ) 
    relay.filter_scanned_drones( [('192.168.137.133', '00:00:00:00:00')] )

