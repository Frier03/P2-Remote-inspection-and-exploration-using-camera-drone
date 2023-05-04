'''The `Drone` and `Relay` class

The implementation of `Drone` and `Relay` classes. 

The `Drone` class represents a drone object, alike to the Tello EDU Drone.
It has attributes such as `name` and `port`.

The `Relay` class represents a relay object that manages a collection of drones
connected to it. It has methods to add and delete drones, and to obtain 
available ports for video streams.
'''


class Drone:
    """Represents a drone object, similar to the Tello EDU Drone.

    Attributes:
        name (str): The name of the drone.
        cmd_queue (list): A command queue for flying the drone.
        port (int | None): The socket port used to send video.
        airborn (bool): A flag indicating whether the drone is currently airborne.
        should_takeoff (bool): A flag indicating whether the drone should take off.
        should_land (bool): A flag indicating whether the drone should land.
        status_information (dict): A dictionary containing information about the drone's status.
    """

    def __init__(self, name) -> None:
        # The name of the drone.
        self.name: str = name

        # Command queue for flying a drone
        self.cmd_queue: list[int, int, int, int] = [0, 0, 0, 0]

        # The Socket Port to send video via.
        self.port: int | None = None

        # To validate the state of a drone
        self.airborn: bool = False
        self.should_takeoff: bool = False
        self.should_land: bool = False

        self.status_information: dict = {}

    def set_status_information(self, status_information: bytes) -> None:
        """Update status information 

        Update the status of a drone. Alike Tello EDU v3

        Args:
            status_information (bytes): The information stream from the drone.  

        Note:
            status_information is alike from a Tello EDU Drone. See Tello Docs for more information        

        Reference:
            [0] [Tello EDU docs V3] (https://dl.djicdn.com/downloads/RoboMaster+TT/Tello_SDK_3.0_User_Guide_en.pdf)
        """
        # What status_information is alike from the Tello
        # “mid:%d;x:%d;y:%d;z:%d;mpry:%d,%d,%d;pitch:%d;roll:%d;yaw:%d;vgx:%d;vgy%d;vgz:% d;templ:%d;temph:%d;tof:%d;h:%d;bat:%d;baro:%f;\r\n”

        # Get every element that we are interested in.
        element = status_information.decode('utf-8').split(';')[5:-1]

        # for every item/status information collected from element.
        for item in element:
            # Get the key, value. for example: "pitch", "32"
            key, value = item.split(':')

            # Overwrite the old status information with the new.
            self.status_information.update({key: value})


class Relay:
    """?

    ? 
    """

    def __init__(
        self,
        name: str,
        active_relays: dict[str, object]
    ) -> None:

        self.name: str = name
        self.drones: dict[str, Drone] = {}
        self.active_relays: dict[str, object] = active_relays
        self.last_heartbeat_received = None # NOTE: Delete? This is never used

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
    drone.set_status_information(
        b'mid:-1;x:-100;y:-100;z:-100;mpry:0,0,0;pitch:0;roll:0;yaw:0;vgx:0;vgy:0;vgz:0;templ:48;temph:50;tof:10;h:0;bat:75;baro:-9.41;time:0;agx:-9.00;agy:-1.00;agz:-998.00;\r\n')
    print(drone.status_information)
