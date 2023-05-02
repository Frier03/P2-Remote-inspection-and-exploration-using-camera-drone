import requests
import subprocess
import re
import threading
import socket
import logging
from time import sleep, time

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

BACKEND_URL = 'http://192.168.137.101:8000/v1/api/relay' # http://ip
ALLOWED_DRONES = ['60-60-1f-5b-4b-ea', '60-60-1f-5b-4b-d8', '60-60-1f-5b-4b-78', '60-60-1f-5b-4c-15', '60-60-1f-5b-4a-0d']

class Relaybox:
    def __init__(self, name, password) -> None:
        self.name = name
        self.password = password #passwork/access to backend
        self.drones = {} #List of drones
        self.token = None

        # Create a used_status_ports list for keeping track of which ports are in use.
        self.used_status_ports = []
        
        #----# Heartbeat variables #----#
        self.session = requests.Session()
        self.heartbeat_url = f"{BACKEND_URL}/heartbeat"
        self.heartbeat_timeout = 10.0 # session timeout (seconds)
        self.heartbeat_interval = 3 # loop interval (seconds)
        self.heartbeat_response_time = 0



        # Socket for checking that multiple drones received commands before changing its ports.
        self.response_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.response_socket.bind(('', 8889))
    

    def connect_to_backend(self) -> None:
        try:
            query = { 'name': self.name, 'password': self.password }
            response = requests.post(f'{BACKEND_URL}/handshake', json=query)
            if response.status_code != 200: # Every HTTPException.
                logging.error(f'Tried connecting to {response.url} | {response.status_code} | Reconnecting in 2 seconds')
                sleep(2)
                self.connect_to_backend()

            token = response.json().get('access_token')
            self.token = token
            logging.info("Connected to backend")
        except Exception:
            logging.error(f'Tried connecting to backend | Reconnecting in 2 seconds')
            sleep(2)
            self.connect_to_backend()
            

    def start(self) -> None:
        logging.info("[THREAD] Scanning for drones...")
        scan_for_drone_thread = threading.Thread(target=self.scan_for_drone, args=())
        scan_for_drone_thread.start()
        heartbeat_thread = threading.Thread(target=self.heartbeat, args=())
        heartbeat_thread.start()


    def heartbeat(self):
        while True:
            start_time = time()
            try:
                query = {"name": self.name}
                response = self.session.get(self.heartbeat_url, json=query, timeout=self.heartbeat_timeout).json()
            except requests.exceptions.Timeout:
                logging.error("Heartbeat timed out")
                continue
            except requests.exceptions.RequestException:
                logging.error("Heartbeat failed")
                continue
            end_time = time()
            self.heartbeat_response_time = end_time - start_time
            backend_data_status = self.backend_data_up_to_date(response) # Check if backend data is up to date with the data we have here
            logging.info(f'Heartbeat | {backend_data_status} | Response time: {self.heartbeat_response_time:.3f} seconds | {self.name}: {self.drones.keys()}')
            
            sleep(self.heartbeat_interval)
    

    def backend_data_up_to_date(self, response):
        up_to_date = True
        for drone_name, drone_data in self.drones.items():
            drone = drone_data['objectId']
            backend_drone_data = response.get(self.name, {}).get('drones', {}).get(drone_name, {})

            if backend_drone_data == {'name': drone.name, 'ports': {'video': drone.video_port}}:
                pass
            else:
                up_to_date = False
 
        for backend_drone_name, backend_drone_data in response.get(self.name, {}).get('drones', {}).items():
            if backend_drone_name not in self.drones:
                up_to_date = False

        if up_to_date:
            return(f"Backend data is up to date for {self.name}")
        else:
            return(f"Backend data is NOT up to date for {self.name}")


    def scan_for_drone(self) -> None: # THREAD!
        while True:
            # The ip is specific for the relays we develop, therefore all drones connected to a relay will have the same first 24bits.
            regex = r"""(192\.168\.137\.[0-9]{0,3}) *([0-9a-z-]*)""" #-Bjørn
            output = str(subprocess.check_output(['arp', '-a']))
            output = output.replace(" \r","")
            scanned_drones = re.findall(regex, output) # [(192.168.137.xxx, 00:00:00:00:00:00), ...] 

            for drone in scanned_drones[:]:
                if drone[1] not in ALLOWED_DRONES:
                    scanned_drones.remove(drone)
            
            # -n is the amount of pings, more is needed for a worse connection.
            for drone in scanned_drones[:]:
                cmd = f"ping -w 100 -n 4 {drone[0]}" 
                pinging = str(subprocess.run(cmd, capture_output=True))
                pinging = pinging.replace(" \r","")

                if "Received = 0" in pinging:
                    scanned_drones.remove(drone)

            self.filter_scanned_drones(scanned_drones)
    

    def filter_scanned_drones(self, scanned_drones):
        # Check for connected drone
        for drone in scanned_drones:
            ips_mapped = []
            for name in self.drones:
                ips_mapped.append(self.drones[name].get('Ip'))

            if drone[0] not in ips_mapped:
                logging.info(f"[CONNECTED] {drone}")
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
                logging.info(f"[DISCONNECTED] {drone.name} {drone.host}")
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
        
        status_port = self.get_status_port()

        # create a class for the drone now
        drone = Drone(name=drone_name, parent=self.name, host=host, status_port=status_port, response_socket=self.response_socket)
        self.drones[drone_name] = { "Ip": host, "objectId": drone }

        drone_thread = threading.Thread(target=drone.start, args=())
        drone_thread.start()


    def delete_drone(self, name) -> None:
        object = self.drones[name].get('objectId')
        self.used_status_ports.remove(object.status_port)

        # Set to False to end the threads: vid, status and command. This has to be done before closing the sockets to avoid a socket error.
        object.drone_active = False

        # Close the status and video socket to allow a new drone to use it.
        object.status_socket.close()
        object.video_socket.close()

        del object
        self.drones.pop(name)


    def disconnected_drone(self, drone: object) -> None:
        query = { 'name': drone.name, 'parent': drone.parent }
        response = requests.post(f'{BACKEND_URL}/drone/disconnected', json=query)

        if response.status_code != 200: # Every HTTPException
            logging.error(f'Error: {response.url} | {response.status_code} | Retrying in 2 seconds')
            sleep(2)
            self.disconnected_drone(drone)
    

    def get_status_port(self) -> int:
        # All 255 usable drone status ports, since its from 3400 to, but not including, 3656 alas a total of 255.
        for status_port in range(50400, 50656):
            
            # Raise exception if the maximum amount of status ports have been used.
            if len(self.used_status_ports) == 255:
                raise ValueError("No available control ports")

            # if the port is not yet used, use i.
            if status_port not in self.used_status_ports:

                # Append port to used_status_ports to keep track of which ports are in use.
                self.used_status_ports.append(status_port)
                return status_port
            
class Drone:
    def __init__(self, name, parent, host, status_port, response_socket) -> None:
        self.name = name
        self.parent = parent
        self.host = host
        self.status_port = status_port
        self.video_port = None #NOTE: video_port for relay -> backend
        
        # Backend video port:
        self.BACKEND_VIDEO_IP = '192.168.137.101'

        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.default_buffer_size = 2048

        # Socket for checking that multiple drones received commands before changing its ports.
        self.response_socket = response_socket

        # Set timeout for response socket
        self.response_socket.settimeout(1)

        # Socket for receiving status from drone.
        self.status_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.status_socket.bind(('', self.status_port))


        self.drone_active = True

        self.takeoff = False


    def start(self):
        logging.info(f"Starting [{self.name}, {self.host}] on {self.parent}")
        
        logging.debug(f"[{self.name}] Getting available video ports from backend...")
        self.get_video_port()
        logging.debug("Got port")

        logging.debug(f"[{self.name}] Entering SDK mode...")        
        self.send_control_command(f"command", self.default_buffer_size)
        logging.debug("Entered SDK mode")

        # Wait 1 seconds for the SDK mode to start.
        sleep(1)

        if self.drone_active == True:
            logging.debug(f"[{self.name}] Telling drone to use port {self.video_port} for streamon...")
            self.set_drone_ports()
            logging.debug(f"{self.name} used {self.video_port} port for streamon")

        """
        # Derelict code
        if self.drone_active == True:
            logging.debug(f"[{self.name}] Sending Handshake Packet to Backend and awaiting response...")
            self.RTS_handshake()
        """

        # Wait 1 seconds for the ports to be correctly set.
        sleep(1)

        if self.drone_active == True:
            self.send_control_command("streamon", self.default_buffer_size)
            self.send_control_command("speed 60", self.default_buffer_size)

            #Start Threads for each process
            logging.debug(f"[{self.name}]: Starting the 4 required threads.")
            video_thread = threading.Thread(target=self.video_thread).start()
            status_thread = threading.Thread(target=self.status_thread).start()
            command_thread = threading.Thread(target=self.rc_thread).start()
            landing_thread = threading.Thread(target=self.landing_thread).start()
            logging.debug(f"[{self.name}]: All threads have started.")


    def status_thread(self):
        # Ask drone for status [battery, yaw, altitude...]
        # Send collected status to API
        
        while self.drone_active == True:
            status, addr = self.status_socket.recvfrom(2048)

            # We do not want to spam the backend, therefore we wait 100ms.
            sleep(0.1)

            query = {'name': self.name, 'parent': self.parent, 'status_information': status.decode('utf-8')}
            requests.post(f'{BACKEND_URL}/drone/status_information', json=query)
    
    def landing_thread(self):
        while self.drone_active == True:

            land_query = { 'name': self.name, 'parent': self.parent }
            should_land = requests.get(f'{BACKEND_URL}/drone/should_land', json=land_query)
            sleep(0.1)
            logging.debug(f'Skal vi lande? {should_land}')

            if '<Response [200]>' == str(should_land):
                self.takeoff = False
                self.send_control_command('land', self.default_buffer_size)

                query = {'name': self.name, 'parent': self.parent }
                status_message = requests.post(f'{BACKEND_URL}/drone/successful_land', json=query)

                logging.debug(f'{self.name} succesfully landed with status: {status_message}')


    def rc_thread(self):

        self.takeoff = False
        takeoff_query = { 'name': self.name, 'parent': self.parent }

        while (self.drone_active == True) and (self.takeoff == False):
            sleep(1)
            try:
                should_takeoff = requests.get(f'{BACKEND_URL}/drone/should_takeoff', json=takeoff_query)
            except:
                logging.error(f'Could not reach {BACKEND_URL}/drone/should_takeoff endpoint, retrying in 2 seconds.')
                sleep(2)
                self.rc_thread()
            
            logging.debug(should_takeoff)

            if '<Response [200]>' == str(should_takeoff):
                takeoff = self.send_control_command('takeoff', self.default_buffer_size)
                logging.debug(f'Completed takeoff for {self.name} at {self.parent}')

                self.takeoff = True
                should_takeoff = requests.post(f'{BACKEND_URL}/drone/successful_takeoff', json=takeoff_query)

            command_queue = { 'name': self.name, 'parent': self.parent}

            # Command queue
            while (self.drone_active == True) and (self.takeoff == True):
                rc_commands = requests.get(f'{BACKEND_URL}/cmd_queue', json=command_queue)

                #logging.debug(rc_commands)

                commands: dict = rc_commands.json()
                commands = commands.get('message')

                #logging.debug(commands)

                drone_command = f'rc {commands[0]} {commands[1]} {commands[2]} {commands[3]}'

                #logging.debug(f'Commands: {drone_commands}')

                self.send_rc_command(drone_command, self.default_buffer_size)

    
    def RTS_handshake(self) -> None:
        # RTS = Ready To Stream

        # Contact backend to tell it we are ready to send video.
        self.video_socket.sendto(b'RTS', (self.BACKEND_VIDEO_IP, self.video_port))
        logging.debug('Send RTS message')

        while self.drone_active == True:
            try:
                data, addr = self.video_socket.recvfrom(32)
                logging.debug('Received RTS message')

                if data:
                    break
            except:
                logging.error('Error receiving confirmation from backend')
        
        if self.drone_active == True:
            logging.debug(f'Completed handshake for {addr}')


    def video_thread(self):
        while self.drone_active == True:
            try:
                video_feed, addr = self.video_socket.recvfrom(self.default_buffer_size)
            except:
                logging.error('Socket have already been closed: 1')

            try:
                # Send video feed to backend, with the specific video feed port, given by the backend in get_video_port().
                self.video_socket.sendto(video_feed, (self.BACKEND_VIDEO_IP, self.video_port))
            except:
                logging.error('Socket have already been closed: 2')
        return
 

    def get_video_port(self):
            query = { 'name': self.name, 'parent': self.parent }
            response = requests.get(f'{BACKEND_URL}/new_drone', json=query)
            
            if response.status_code != 200: # Every HTTPException.
                logging.error(f"Error trying to get available port from URL [{response.url}] with status code {response.status_code}")
                sleep(2)
                self.get_video_port()
                
            
            port = response.json().get('video_port')
            self.video_port = port


    def set_drone_ports(self):
        # the ip should be set '', but when running it on a local machine this socket address is already 
        # being used by the video_server class.
        self.video_socket.bind(('', self.video_port))
        self.send_control_command(f"port {self.status_port} {self.video_port}", self.default_buffer_size)
    

    def send_control_command(self, command: str, buffer_size: int) -> None:
        try:
            while self.drone_active == True:
                
                response = None
                addr = None

                try:
                    # Send command and await response.
                    logging.debug(f'Sending command: {command} to {self.name} at {self.host} and awaiting response.')
                    self.response_socket.sendto(bytes(command, 'utf-8'), (self.host, 8889)) 
                    response, addr = self.response_socket.recvfrom(buffer_size)
 
                except OSError:
                    logging.debug(f'Error did not receive response from {self.name} at {self.host}, resending new command: {command} in 2s.')
                    sleep(2)
                    ...

                if response != None:
                    logging.debug(f'Received response: {response} from {self.name} at {self.host}')
                    decoded_response = response.decode('utf-8')
                    
                    if ('ok' == decoded_response) and (addr[0] == self.host):
                        logging.debug(f'{self.name}, returned ok')
                        return True
                
                logging.debug('No response was received in the given time.')

        except Exception as socket_error:
            logging.error(f'Error: {socket_error}')
            

    def send_rc_command(self, command: str, buffer_size: int) -> None:
        try:
            # Send command and do not await response.
            logging.debug(f'Sending command: {command} to {self.name} at {self.host}.')
            self.response_socket.sendto(bytes(command, 'utf-8'), (self.host, 8889)) 

        except OSError:
            pass # The only error that can occur is when the socket is closed by another thread, we catch this expection, but do nothing with it.

if __name__ == '__main__':
    relay = Relaybox("relay_0001", "123")
    relay.connect_to_backend()
    relay.start()