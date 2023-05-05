'''The main program for the relaybox.

The purpose of this Python program is to abstract the communication from a
drone to the backend. 

Outline:
    - Relaybox (class): A class for handling drones.
    - Drone (class): A interface for the Relay class to interact with.

Notes:
    The Python program only works on Windows computers. 
    It has only been tested with Windows 10.
'''

import requests, subprocess, re, threading, socket, logging
from time import sleep, time

# Setup the logging module
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

# The URL of the backend IPv4.
BACKEND_URL = 'http://89.150.129.29:8000/v1/api/relay'

class Relaybox:
    """The model of a relaybox, allows multiple drones to connect, by contacting a backend server.

    Example:
        >>> if __name__ == '__main__':
                relay = Relaybox("relay_0001", "123")
                relay.backend_authentication()
                relay.start()
    """
    def __init__(self, name: str, password: str) -> None:
        """Creates a relaybox based on a name and a password.

        Arguments:
            name (str): The name of the relaybox.
            password (str): The password of the relaybox, used to access the backend. This should match an entry in mongoDB.
        """
        
        self.NAME: str = name
        self.PASSWORD: str = password
        self.token: str | None = None 
        self.session: requests.Session = requests.Session() # Used for the heartbeat function only. Token did not work

        # Dict of drones currently connected to the relaybox
        self.drones: dict[Drone.name: dict[Drone.IP: id(Drone)]] = {}

        # Authorized drones on all relay boxes via the Tello EDU drones MAC addresses.
        self.AUTHORIZED_DRONES: list[str] = [
            '60-60-1f-5b-4b-ea',
            '60-60-1f-5b-4b-d8', 
            '60-60-1f-5b-4b-78', 
            '60-60-1f-5b-4c-15', 
            '60-60-1f-5b-4a-0d'
        ]
    
        # A list for keeping track of all status ports that are in use. 
        self.used_status_ports: list[int] = []
        
        # Socket for listing for possible reponses from the Tello drones. See thier docs for more detail.
        self.response_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.response_socket.bind(('', 8889))


    def backend_authentication(self) -> None:
        """Connects to backend, based on the backend IP, the relay name and password."""

        # Try to authenticate with backend.
        try:
            # Authenticate with backend at the endpoint handshake, with a http query.
            query: dict = { 'name': self.NAME, 'password': self.PASSWORD }
            response = requests.post(f'{BACKEND_URL}/handshake', json=query)
            
            # If we could not logon.
            if response.status_code != 200:
                logging.error(f'Tried connecting to {response.url} | {response.status_code} | Reconnecting in 2 seconds')
                sleep(2)
                self.backend_authentication()

            token: str = response.json().get('access_token')
            self.token = token
            logging.info("Connected to backend")
            
        # When no reponse is given try again.
        except Exception:
            logging.warning(f'Tried connecting to backend | Reconnecting in 2 seconds')
            sleep(2)
            self.backend_authentication()
            

    def start(self) -> None:
        """Start scaning for drones and start heartbeat with backend
        
        Starts a thread that only checks for Tello Drones.
        It also starts a thread for heartbeat with backend.

        Notes:
            Call this after authentication with backend.
        
        """

        logging.info("[THREAD] Scanning for drones...")
        scan_for_drone_thread = threading.Thread(target=self.scan_for_drone, args=())
        scan_for_drone_thread.start()

        # Start a new thread with the heartbeat
        logging.info("[THREAD] Starting heartbeat...")
        heartbeat_thread = threading.Thread(target=self.heartbeat, args=())
        heartbeat_thread.start()


    def heartbeat(self, interval: int = 3) -> None:
        """Maintain a connection with the backend.

        Maintains a connection for the relaybox so that is does not time out.
        This is used so that the backend knows the status of the relaybox.
        It also updates the backend with new information about its connected Tello drones
        """
        HEARTBEAT_URL: str = f"{BACKEND_URL}/heartbeat"
        
        # Time it takes the heartbeat to repond
        response_time: float | None = None

        while True:
            start_time = time()
            
            try:
                query = { 'name': self.NAME }
                response = self.session.get(HEARTBEAT_URL, json=query, timeout=10.0).json()
                
            except requests.exceptions.Timeout:
                logging.error("Heartbeat timed out")
                continue
            
            except requests.exceptions.RequestException:
                logging.error("Heartbeat failed")
                continue
            
            end_time = time()
            response_time = end_time - start_time

            # Check if backend data is up to date with the data the relay has
            backend_data_status: str = self.backend_data_up_to_date(response)
            logging.info(f'Heartbeat | {backend_data_status} | Response time: {response_time:.3f} seconds | {self.NAME}: {self.drones.keys()}')
            
            sleep(interval)
    

    def backend_data_up_to_date(self, response: dict) -> str:
        """Checks if the backend has the most up-to-date information on the drones.

        Arguments:
            response (dict): reponse from backend as `RelayHeartbeatModel`

        Returns:
            str: A message indicating whether the backend is up to date or not.

        Example:
            This method can be used to check if the drone data stored in a relay object is in sync with the 
            data stored in the backend. For example:

            >>> response = {
                    "message": f"Hello {relay.name}",
                    f"{relay.name}": {
                        "drones": relay.drones
                    } 
                }
            >>> relay.backend_data_up_to_date(response)
            "Backend data is up to date for <relay_name>"

        """
        # Initialize up_to_date flag as True
        up_to_date: bool = True

        # Compare drone data in the relay object with that in the backend response
        for drone_name, drone_data in self.drones.items():
            drone: Drone = drone_data['objectId']
            backend_drone_data = response.get(self.NAME, {}).get('drones', {}).get(drone_name, {})
            relay_drone_data = {'name': drone.name, 'ports': {'video': drone.video_port}}

            # If there is a discrepancy between the Relay and the backend.
            if backend_drone_data != relay_drone_data:
                up_to_date = False

        # Check if the backend contains any drones that are not in the relay object
        backend_drones_data: dict = response.get(self.NAME, {}).get('drones', {}).items()

        for backend_drone_name, backend_drone_data in backend_drones_data:
            if backend_drone_name not in self.drones:
                up_to_date = False

        # Return a message indicating whether the backend is up to date or not
        if up_to_date:
            return f"Backend data is up to date for {self.NAME}"
        
        return f"Backend data is NOT up to date for {self.NAME}"


    def scan_for_drone(self) -> None:
        """
        Scans the local network for drones and filters out unauthorized and
        unresponsive drones. Adds authorized drones to the relay's list of drones.

        This method is used in a thread to constantly scann the 
        local network for Tello EDU Drones.
        
        Note:
            This has only been tested on Windows 10.
            Other OS has not been tested.

        Examples:
            Here a `arp -a` has been used with Microsoft CMD.

            >>> Interface: 192.168.1.101 --- 0xe
                    Internet Address      Physical Address      Type
                    192.168.1.1           ##-##-##-##-##-##     dynamic
                    192.168.1.255         ff-ff-ff-ff-ff-ff     static
                    224.0.0.22            01-00-5e-00-00-16     static
                    224.0.0.251           01-00-5e-00-00-fb     static
                    224.0.0.252           01-00-5e-00-00-fc     static
                    239.255.255.250       01-00-5e-7f-ff-fa     static
                    255.255.255.255       ff-ff-ff-ff-ff-ff     static
            
            A example of the `ping -w 100 -n 4 127.0.0.1`

            >>> Pinging 127.0.0.1 with 32 bytes of data:
                    Reply from 127.0.0.1: bytes=32 time<1ms TTL=128
                    Reply from 127.0.0.1: bytes=32 time<1ms TTL=128
                    Reply from 127.0.0.1: bytes=32 time<1ms TTL=128
                    Reply from 127.0.0.1: bytes=32 time<1ms TTL=128

                    Ping statistics for 127.0.0.1:
                        Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
                    Approximate round trip times in milli-seconds:
                        Minimum = 0ms, Maximum = 0ms, Average = 0ms
        """
        while True:
            # The First 3 numbers in the IPv4 does not change on Windows when HotSpot is active.
            # The last part of the regex is to find the MAC. NOTE: that on windows `-` are used to separate in the MAC.
            # The ´type´ is not important.  
            regex = r"""(192\.168\.137\.[0-9]{0,3}) *([0-9a-z-]*)"""
            
            # Run CMD command `arp -a`, to get all current connections.
            output: str = str(subprocess.check_output(['arp', '-a']))
            output: str = output.replace(" \r","")
            scanned_drones: list[tuple(str, str)] = re.findall(regex, output) # [(192.168.137.xxx, 00:00:00:00:00:00), ...] 

            # Filter out unauthorized drones as drone[1] by comparing their MAC addresses with the AUTHORIZED_DRONES list.
            for drone in scanned_drones[:]:
                if drone[1] not in self.AUTHORIZED_DRONES:
                    scanned_drones.remove(drone)
            
            # Loop through all authorized drones with `ping`, where `-w` is the maximum response time, `-n` is the amount of pings, `drone[0]` is the IP of the Tello drone.
            for drone in scanned_drones[:]:
                cmd: str = f"ping -w 100 -n 4 {drone[0]}" 
                pinging: str = str(subprocess.run(cmd, capture_output=True))
                pinging: str = pinging.replace(" \r","") 

                # If no ping (ICMP) was successful remove the drone, since it must not be on the network anymore.
                if "Received = 0" in pinging:
                    scanned_drones.remove(drone)

            self.filter_scanned_drones(scanned_drones)
    

    def filter_scanned_drones(self, scanned_drones: list) -> None:
        """
        Filters the list of scanned drones and adds new drones to the relay's list of drones, or removes disconnected drones.

        Arguments:
            scanned_drones (list): A list of tuples containing the IP addresses and MAC addresses of the scanned drones.
        """
        # Check for connected drone
        for drone in scanned_drones:
            # Create a list of IP addresses of currently connected drones.
            IPs_mapped: list = []

            for name in self.drones:
                IPs_mapped.append(self.drones[name].get('IP'))

            # If the scanned drone is not in the list of connected drones, add it to the relay's list of drones with the add_drone()
            if drone[0] not in IPs_mapped:
                logging.info(f"[CONNECTED] {drone}")
                self.add_drone(drone[0])
        
        # Append the connected drone to a list containing all object ids of the drones.
        drones_object_list: list[dict[str: (str, id(Drone))]] = []
        for name in self.drones:
            drones_object_list.append(self.drones[name].get('objectId'))

        
        for drone in drones_object_list:
            # resest the list of IP addresses of currently scanned drones
            IPs_mapped: list = []

            for drone_IP in scanned_drones:
                IPs_mapped.append(drone_IP[0])
                
            # If the IP address of the drone is not in the list of scanned drones, remove it from the relay's list of drones
            if drone.host_IP not in IPs_mapped:
                logging.info(f"[DISCONNECTED] {drone.name} {drone.host_IP}")
                self.delete_drone(drone.name)
                self.disconnected_drone(drone)


    def add_drone(self, host_IP: str) -> None:
        """
        Adds a new drone to the RelayBox's list of active drones.

        This method creates a new Drone object, generates a unique name for it based on the IP address, 
        and starts a new thread to handle the drone's communication. The new drone is added to the RelayBox's 
        list of active drones with its IP address and object ID.

        Arguments:
            host_IP (str): The IP address of the drone to be added.
        """
        # Find a unique name for the drone
        used_names = []

        # Add connected drone's name to a list with used_names so we do not get duplicates
        for drone in self.drones.keys():
            used_names.append(drone)
        
        # Since tello utilizes the last 8 bits of the IP header, we can have a total of 254 IPs, excluding the router's own.
        for num in range(1, 254):
            if "drone_{:03d}".format(num) not in used_names:
                drone_name = "drone_{:03d}".format(num)
                break
        else:
            raise ValueError('No Available names for new drone')
        
        # Get a status port for the specfic drone
        status_port = self.get_status_port()

        # create a new drone object now
        drone = Drone(
            name=drone_name, 
            parent=self.NAME, 
            host_IP=host_IP, 
            status_port=status_port, 
            response_socket=self.response_socket
        )

        # Append the new created drone to the relayboxs list of active drones.
        self.drones[drone_name]: dict = { "IP": host_IP, "objectId": drone }

        # Create a new thread for the added drone to communicate to it.
        drone_thread = threading.Thread(target=drone.start, args=())
        drone_thread.start()


    def delete_drone(self, name: str) -> None:
        """Delete a drone, that is no longer connected to the relaybox.
        
        Arguments:
            name (str): The name of the drone, like `drone_001`
        """
        # Get the object id from the name, by looking in the self.drone dictionary.
        object: Drone = self.drones[name].get('objectId')

        # Remove the status port so it can be re-used.
        self.used_status_ports.remove(object.status_port)

        # Set to False to end the threads: video, status, rc and land. This has to be done before closing the sockets to avoid a socket error.
        object.drone_active: bool = False

        # Close the status and video socket to allow a new drone to use it.
        object.status_socket.close()
        object.video_socket.close()

        # Delete the drone object from memory
        del object

        # Now remove it from the relays list of active drones.
        self.drones.pop(name)


    def disconnected_drone(self, drone: object) -> None:
        """Update the backend, that a drone has been disconnted from the local network.

        Arguments:
            drone (Drone): A drone object.
        """
        # Post to the backend endpoint to tell it that the drone have disconnected.
        query = { 'name': drone.name, 'parent': drone.parent }
        response = requests.post(f'{BACKEND_URL}/drone/disconnected', json=query)

        # If the responescode was not OK.
        if response.status_code != 200:
            # Try again
            logging.error(f'Error: {response.url} | {response.status_code} | Retrying in 2 seconds')
            sleep(2)
            self.disconnected_drone(drone)
    

    def get_status_port(self) -> int:
        """Get an available status port for the drone.

        Notes:
            The status is a part of the Tello EDU drone. See thier docs for more detail.
        """
        # All 254 usable drone status ports, since the range is from 50400 to 50655, but not including it, which equals a total of 254 ports.
        for status_port in range(50400, 50655):
            
            # Raise exception if the maximum amount of status ports have been used.
            if len(self.used_status_ports) >= 254:
                raise ValueError('No available control ports')

            # if the port is not yet used, use it.
            if status_port not in self.used_status_ports:

                # Append port to used_status_ports to keep track of which ports are in use.
                self.used_status_ports.append(status_port)

                # Return the port that should be used to receive status from the drone.
                return status_port
            
class Drone:
    """A model of a Tello drone

    The purpose of this class to to have a interface for a relay to talk to. 
    It is like the offcial Tello EDU API, but does not share any codebase.

    Reference:
        [0] [Tello EDU Docs]   
    """
    def __init__(self, name: str, parent: str, host_IP: str, status_port: int, response_socket: socket.socket) -> None:
        """Creates a drone based on a name, a parrent (relaybox), host_IP, status_port and a socket.

        Arguments:
            name (str): The name of the drone.
            parent (str): The name of the relaybox.
            host_IP (str): The IP of the drone.
            status_port (int): The port that the drone should send status messages to.
            response_socket (socket.socket): A socket for receiving a response when a command have been sent.
        """
        self.name: str = name
        self.host_IP: str = host_IP
        self.video_port: int | None = None 
        self.status_port: int = status_port

        # The relaybox that the drone belongs to.
        self.parent: str = parent
        
        # The IPv4 address for the backend.
        self.backend_IP = '89.150.129.29' # TODO: This could be an URL instead

        # A UDP socket for receiving the video feed from the drone.
        self.video_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.buffer_size: int = 2048

        # Socket for checking that multiple drones received commands before changing its ports.
        self.response_socket: socket.socket = response_socket

        # Set timeout for response socket in seconds 
        self.response_socket.settimeout(1)

        # A UDP socket for receiving status from drone.
        self.status_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4 UDP
        self.status_socket.bind(('', self.status_port))

        # Flags for the drone's state.
        self.drone_active: bool = True
        self.takeoff: bool = False


    def start(self) -> None:
        """Starts the necesary logic for the drone to connect to the backend and a client.
        
        Starts mutliple threads that get a video feed, drone status, if the drone should land and the commands it should perform.
        It also starts a thread for heartbeat with backend.

        Note:
            The many if statments are there to not go through code after the drone have diconnected, 
            since this happens in another thread in the Relaybox class.
            This method is called after `add_drone()` in the Relaybox
        """
        logging.info(f"Starting [{self.name} at {self.host_IP}] on {self.parent}")
        
        logging.debug(f"[{self.name}] Getting available video ports from backend...")
        self.get_video_port()
        logging.debug(f"Got port: {self.video_port}")

        logging.debug(f"[{self.name}] Entering SDK mode...")        
        self.send_control_command("command")
        logging.debug(f"[{self.name}] Entered SDK mode")

        # Wait 1 seconds for the SDK mode to start. (Tello limitation)
        sleep(1)

        if self.drone_active:
            logging.debug(f"[{self.name}] Telling drone to use port {self.video_port} for streamon...")
            self.set_drone_ports()
            logging.debug(f"{self.name} used {self.video_port} port for streamon")

        # Ready To Stream (RTS) handshake with backend
        if self.drone_active:
            logging.debug(f"[{self.name}] Sending Handshake Packet to Backend and awaiting response...")
            self.RTS_handshake()
        
        # Wait 1 seconds for the ports to be correctly set. (Tello limitation)
        sleep(1)

        # Now that we have a status and video port, begin to stream
        self.send_control_command("streamon")

        # Set the speed of the Tello, the default value is rather low, so we set it higher
        # NOTE: See Tello EDU docs about speed interval.
        self.send_control_command("speed 60")
        
        if self.drone_active:
            #Start Threads for each process
            logging.debug(f"[{self.name}]: Starting the 4 required threads.")

            video_thread = threading.Thread(target=self.video_thread).start()
            status_thread = threading.Thread(target=self.status_thread).start()
            rc_thread = threading.Thread(target=self.rc_thread).start()
            landing_thread = threading.Thread(target=self.landing_thread).start()
            
            logging.debug(f"[{self.name}]: All threads have started.")


    def status_thread(self) -> None:
        """A Thread for handling the drone's status
    
        This method runs on a separate thread and listens for status updates from the drone.
        When it receives a status update, it sends the information to the backend.
        """
        # Continuously listen for status updates while the drone is active.
        while self.drone_active:
            
            # Receive the status update and the address it came from.
            status, addr = self.status_socket.recvfrom(self.buffer_size)

            # We do not want to spam the backend, therefore we wait 100ms.
            sleep(0.1)

            # Post the status to a backend endpoint.
            query = {'name': self.name, 'parent': self.parent, 'status_information': status.decode('utf-8')}
            requests.post(f'{BACKEND_URL}/drone/status_information', json=query)
    
    
    def landing_thread(self) -> None:
        """Check if the drone should land.

        Continuously checks with the backend server to see if the drone should land. 
        """

        # Continuously listen for status updates while the drone is active.
        while self.drone_active == True:

            land_query = { 'name': self.name, 'parent': self.parent }
            should_land = requests.get(f'{BACKEND_URL}/drone/should_land', json=land_query)
            sleep(0.1)

            # If the backend indicates that the drone should land
            if '<Response [200]>' == str(should_land):
                self.takeoff = False
                self.send_control_command('land')

                query = {'name': self.name, 'parent': self.parent }
                status_message = requests.post(f'{BACKEND_URL}/drone/successful_land', json=query)

                logging.debug(f'{self.name} succesfully landed with status: {status_message}')


    def rc_thread(self) -> None:
        """Sends commands to the drone received from the backend.

        Continuously checks with the backend server to see if it should land
        and updates its commands for controlling the drone.

        """
        self.takeoff: bool = False


        while self.drone_active and self.takeoff:

            # Query backend server to check if drone should take off
            takeoff_query: dict = { 'name': self.name, 'parent': self.parent }

            # Sleep so that we do not spam the backend server.
            sleep(1)

            # Try to check it the drone should takeoff
            try:
                should_takeoff = requests.get(f'{BACKEND_URL}/drone/should_takeoff', json=takeoff_query)

            # If it fails to do so
            except Exception:
                # Wait and repeat.
                logging.error(f'Could not reach {BACKEND_URL}/drone/should_takeoff endpoint, retrying in 2 seconds.')
                sleep(2)
                self.rc_thread()

            # If the resopns was successful.
            if '<Response [200]>' == str(should_takeoff):

                # The drone should now takeoff
                self.send_control_command('takeoff')
                logging.debug(f'Completed takeoff for {self.name} at {self.parent}')

                # Update the takeoff flag.
                self.takeoff = True

                # Update the backend statues of the drone about the takeoff.
                should_takeoff = requests.post(f'{BACKEND_URL}/drone/successful_takeoff', json=takeoff_query)

            # Now we check for controls from the backend.
            command_queue: dict = { 'name': self.name, 'parent': self.parent}

            # The reason for having the same while loop is because the drone
            # may become inactive. The while loop is to more quickly return if a drone is diconnected. 
            # This saves a small amount of resource.
            while self.drone_active and self.takeoff:
                # Get commands from the backend endpoint: cmd_queue.
                rc_commands: dict = requests.get(f'{BACKEND_URL}/cmd_queue', json=command_queue).json()

                # { 'message': [1, 2, 3, 4]}
                commands: list = rc_commands.get('message')
                
                # Create a string that we can pass directly to the drone.
                drone_command = f'rc {commands[0]} {commands[1]} {commands[2]} {commands[3]}'

                # Send the received command to the Tello drone.
                self.send_rc_command(drone_command)

    
    def RTS_handshake(self) -> None:
        """Perform a handshake with the backend to establish a drone's readiness to send video.

        Sends an Ready To Stream message to the backend to indicate that the drone is ready to stream video.
        """

        self.video_socket.settimeout(2)

        while self.drone_active:
            # RTS = Ready To Stream
            try:
                # Send an RTS message to the backend to indicate that the drone is ready to stream video.
                self.video_socket.sendto(b'RTS', (self.backend_IP, self.video_port))
                logging.debug('Send an RTS message')
            except OSError as error:
                logging.debug(f'{error}, socket have already been closed.')

            try: 
                # We are only receving a flag, so a buffer of 32 is more than sufficient.
                data, addr = self.video_socket.recvfrom(32)

                # If we get permission from the backend.
                if data:
                    logging.debug('Received RTS message')
                    break
                else:
                    logging.debug('Did not receive confirmation of RTS, resending in 2sec ...')
                    sleep(2)

            except:
                logging.error('Error receiving confirmation from backend')
                sleep(2)
            
        if self.drone_active:
            logging.debug(f'Completed handshake for {addr}')


    def video_thread(self) -> None:
        """Send video from the drone to the backend.
        
        A thread for streaming video feed from the drone to the backend.

        This method continuously receives video feed from the drone over a socket connection and sends it to the backend
        over the same socket connection. The specific video feed port to use is obtained from the backend by calling
        get_video_port(). The function runs until self.drone_active is set to False.
        """
        while self.drone_active:
            try:
                # Retrive the video feed from the Tello drone
                video_feed, addr = self.video_socket.recvfrom(self.buffer_size)

            except Exception:
                logging.error(f'Socket have already been closed: {addr}')

            try:
                # Now send that video to the backend
                self.video_socket.sendto(video_feed, (self.backend_IP, self.video_port))

            except Exception:
                logging.error(f'Socket have already been closed: {addr}')
 

    def get_video_port(self) -> None:
        """Gets a video port from the backend
        """
        query: dict = { 'name': self.name, 'parent': self.parent }
        response = requests.get(f'{BACKEND_URL}/new_drone', json=query)
        
        if response.status_code != 200: # TODO: THIS IS THE RIGHT WAY OF CHECKING HTTP CODES
            logging.error(f"Failed trying to get available port from URL [{response.url}] with status code {response.status_code}")

            # If we did not get a video port.
            if self.drone_active:
                # try again.
                sleep(2)
                self.get_video_port()
            
        # Update the drones video port.
        port: int = response.json().get('video_port')
        self.video_port = port


    def set_drone_ports(self) -> None:
        """Set drone status and video ports.

        Send a command to the drone to configure its status_port and video_port.        
        """
        # Bind the video_socket to the given video port, given by the backend server.
        self.video_socket.bind(('', self.video_port)) 

        # Send a SDK command to tell the Tello drone to change its status and video feed ports.
        self.send_control_command(f"port {self.status_port} {self.video_port}")
    

    def send_control_command(self, command: str) -> bool | None:
        """Send a command to the drone with reurn.

        Arguments:
            command (str): The command to send to the drone.

        Example:
            >>> send_control_command('speed 60')
            True

        Notes:
            The command must be of same format as the Tello EDU Drone.
            Se Tello EDU docs for more detail.
        
        """

        # Try everything because the drone may disconnect without notifying us.
        try:
            # As long the drone is active.
            while self.drone_active:
                
                # Define `response` and `addr` for error handling
                response = None
                addr = None

            
                try:
                    # Send command and await response.
                    logging.debug(f'Sending command: {command} to {self.name} at {self.host_IP} and awaiting response.')

                    # Send the command to the drone.
                    self.response_socket.sendto(
                        bytes(command, 'utf-8'), # Default formatring for the Tello drone
                        (self.host_IP, 8889) # The default command port for the Tello EDU drone
                    ) 

                    # Await its response.
                    response, addr = self.response_socket.recvfrom(self.buffer_size)
 
                # The OS may not be able to send via the socket at that moment, so we log.
                except OSError:
                    logging.debug(f'Error did not receive response from {self.name} at {self.host_IP}, resending new command: {command} in 2s.')
                    sleep(2)

                # If we get a response from the drone.
                if response != None:
                    logging.debug(f'Received response: {response} from {self.name} at {self.host_IP}')
                    decoded_response = response.decode('utf-8')
                    
                    # Check if we receive and 'ok' and its on the right IP.
                    if ('ok' == decoded_response) and (addr[0] == self.host_IP):
                        logging.debug(f'{self.name}, returned ok')
                        return True
                
                # Otherwise the response was not received in time.
                logging.debug('No response was received in the given time.')

            # In the case the we try to send a command to a drone, that is not active.
            if not self.drone_active:
                logging.debug('Connection to drone lost.')

        # Log every error.
        except Exception as error:
            logging.error(f'Error: {error}')
            

    def send_rc_command(self, command: str) -> None:
        """Send a command without a respones
        
        Arguments:
            command (str): A command to send to the drone.

        Notes:
            The command must be of same format as the Tello EDU Drone.
            Se Tello EDU docs for more detail.
        """
        try:
            # Send command and await response.
            logging.debug(f'Sending command: {command} to {self.name} at {self.host_IP}.')

            # Send the command to the drone.
            self.response_socket.sendto(bytes(command, 'utf-8'), (self.host_IP, 8889)) 

        except OSError as error:
            logging.error(f'{error}, socket have already been closed.')

if __name__ == '__main__':
    relay = Relaybox("relay_0001", "123")
    relay.backend_authentication()
    relay.start()