class Drone:
    def __init__(self, name) -> None:
        self.name: str = name
        self.cmd_queue: list = []
        self.port: int = None
        self.airborn: bool = False
        self.should_takeoff: bool = False
        self.should_land: bool = False 

        self.status_information: dict = {}
        
    
    def set_status_information(self, status_information: bytes) -> None:
        
        element = status_information.decode('utf-8').split(';')[5:-1]

        for item in element:
            key, value = item.split(':')
            self.status_information.update({key: value})
class Relay:
    def __init__(self, name, active_relays):
        self.name = name
        self.drones = {}
        self.active_relays = active_relays
        self.last_heartbeat_received = None

    def add_drone(self, name):
        # Check for available ports
        used_ports = set()
        for relay in self.active_relays.values():
            for drone in relay.drones.values():
                used_ports.add(drone.port)

        # usable ports for video streams.
        for port in range(52222, 53334):
            if port not in used_ports:
                video_port = port
                break
        else:
            raise ValueError("All available ports are taken.")

        # Create new Drone instance
        drone = Drone(name)
        drone.port = video_port
        self.drones[name] = drone

        return video_port
    
    def delete_drone(self, name):
        pass




'''
if __name__ == '__main__':
    # New relay connects { "name": "Relay_4444" }
    relay0001 = Relay("Relay_0001")
    relay0002 = Relay("Relay_0002")
    relay0003 = Relay("Relay_0003")
    
    # New drone has connected to Relay_0002
    for i in range(300):
        if i == 10:
            first_drone_name = next(iter(relay0002.drones.keys()))
            del relay0002.drones[first_drone_name]
            print(f"Removed first drone {first_drone_name}")
        elif i == 20:
            drone_names = list(relay0002.drones.keys())
            fourteenth_drone_name = drone_names[13]
            del relay0002.drones[fourteenth_drone_name]
            print(f"Removed 14th drone {fourteenth_drone_name}")
        
        ports = relay0002.add_drone(f"drone_{i}")
        print(ports)
        from time import sleep
        sleep(2)

'''

if __name__ == '__main__':
    drone = Drone("bruh_drone")
    drone.set_status_information(b'mid:-1;x:-100;y:-100;z:-100;mpry:0,0,0;pitch:0;roll:0;yaw:0;vgx:0;vgy:0;vgz:0;templ:48;temph:50;tof:10;h:0;bat:75;baro:-9.41;time:0;agx:-9.00;agy:-1.00;agz:-998.00;\r\n')
    print(drone.status_information)