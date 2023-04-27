class Drone:
    def __init__(self, name):
        self.name = name
        self.cmd_queue = []
        self.port = None

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
                used_ports.update(drone.port)

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