class Relay:
    def __init__(self, name) -> None:
        self.name = name
        self.drones = {}
        
    def add_drone(self, name):
        drone = Drone(name)
        self.drones[name] = drone


class Drone:
    def __init__(self, name) -> None:
        self.name = name


if __name__ == '__main__':
    # New relay connects { "name": "Relay_4444" }
    relay = Relay("Relay_4444")