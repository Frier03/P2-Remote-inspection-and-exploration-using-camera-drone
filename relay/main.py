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
        self.drones = []
        self.token = None
    
    def connect_to_backend(self) -> None:
        response = requests.post(f'{BACKEND_URL}/v1/auth/relay/handshake', json={ 'name': self.name, 'password': self.password})
        token = response.json().get('access_token')
        self.token = token

    def post_drones_to_backend(self) -> None:
        
        ...

    def add_drone(self) -> None:
        # find a unique name for the drone
        # create a class for the drone now
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
        # how to know if a drone is connected? if we have a drone in scanned_drones, that is not a part of self.drones
        for drone in scanned_drones:
            if drone not in self.drones:
                print(f"[CONNECTED] {drone}")
                self.drones.append(drone)
        
        # how to know if a drone is disconnected? if we have a drone in self.drones, that is not a part of scanned_drones
        for drone in self.drones:
            if drone not in scanned_drones:
                print(f"[DISCONNECTED] {drone}")
                self.drones.remove(drone)

    def heartbeat(self, callback) -> None:
        scan_for_drone_thread = threading.Thread(target=scan_for_drone_thread, args=(callback,))
        scan_for_drone_thread.run()
        
    



class Drone:
    def __init__(self, name, parent) -> None:
        self.name = name
        self.parent = parent

if __name__ == '__main__':
    relay = Relaybox("relay_0001", "123")
    #relay.connect_to_backend()
    #relay.heartbeat(relay.filter_scanned_drones)

    relay.drones = [("192.168.137.123", "mac her"), ("192.168.137.243", "mac her 2")]
    relay.filter_scanned_drones( [("192.168.137.123", "mac her")] ) # scan_drones calls this function with a list of scanned drones. We just hardcoded one scanned drone in, for testing...
