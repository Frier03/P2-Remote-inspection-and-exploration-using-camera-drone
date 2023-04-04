class Relay:
    def __init__(self, name) -> None:
        self.name = name
        self.drones = []



class Drone:
    def __init__(self, name) -> None:
        self.name = name
        self.cmd_queue: list = None
        self.video_feed_string: str = None
        



if __name__ == '__main__':
    # New relay connects { "name": "Relay_4444" }
    relay = Relay("Relay_4444")


    """
    New drone connects: Relay --> Backend (/v1/api/relay?=name/new_drone)
    
    """