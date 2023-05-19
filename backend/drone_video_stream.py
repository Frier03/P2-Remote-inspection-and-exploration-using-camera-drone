'''A file for streaming video for a drone

This file defines a `DroneVideoStream` class which allows for streaming video from a drone. 
It uses UDP and IPv4 to connect with clients and starts streaming video once two clients have connected.
The class contains methods for binding the socket and waiting for connections from clients, sending and receiving data with the connected clients, and handling any errors that may occur during the process.
The class also has attributes for storing the video port, socket object, and a list of connected clients.
'''
import threading, socket

class DroneVideoStream:
    """
    A DroneVideoStream class for streaming video for a drone.

    Attributes:
        video_port (int): The port for the video stream.
        socket (socket.socket | None): The socket used for the video stream.
        active (bool): A flag indicating if the video stream is currently active.
        connections (list): A list of tuples representing the active connections. Each
            tuple contains the IP address and port number of a connected client.
    """
    
    def __init__(self, video_port) -> None:
        print("Initializing Video Server")
        self.video_port = video_port 
        self.socket: socket.socket | None = None
        self.active: bool = True
        self.connections: list = [] # example `[(192.168.137.1, 52222), (..., ...), ...]`
        video_stream: threading.Thread = threading.Thread(target=self.start, args=())
        video_stream.start()

    def start(self) -> None:
        """
        Bind a UDP socket to a specific IP address and port number for video streaming.
        
        This method gets the hostname of the computer running the code and uses the `socket.gethostbyname()` method
        to get the IP address associated with the hostname. It then creates a socket object with the IPv4 protocol
        and the UDP protocol and binds it to the obtained IP address and the port number specified by `self.video_port`.
        
        This method also calls the `check_conn()` method to listen for incoming connections and start the video stream.
        """
        # Create address from IPv4 and port
        print(self.video_port)
        ADDRESS = ('', self.video_port)
        
        # Create socket and bind
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # IPv4 with UDP
        self.socket.bind(ADDRESS) # Bind socket to ADDRESS
        
        self.check_conn()


    def handle_stream(self) -> None:
        """Sends and receives data with the connected clients.

        Sends confirmation packets to each client to confirm their connection, then enters a loop
        where it waits for data from one of the clients and sends that data to the other client.

        Raises:
            Exception: If the socket is closed or the client is disconnected.
        """

        # Send confirmation packets to both clients
        for address in self.connections:
            self.socket.sendto("hello drone".encode('utf-8'), address)


        # While both clients are connected and the stream is active
        while self.active:
            try:
                # Receive data from one of the clients
                data, addr = self.socket.recvfrom(2048)

            except Exception:
                print('Could not retrieve message/Timeout: Socket Most Likely Closed.')
                return
            
            try:
                # Send the data to the other client
                for address in self.connections:
                    if address != addr:
                        try:
                            self.socket.sendto(data, address)
                        except Exception:
                            print("Could not send data to client.")
            except Exception:
                return
        return


    def check_conn(self) -> None:
        print("Checking Connections for Drone")
        """Waits for two clients to connect.

        Continuously listens for data from clients until two clients have connected, then calls
        handle_stream to start sending and receiving data.

        Raises:
            Exception: If the socket is closed.
        """
        address = None
        # Wait for two clients to connect
        while len(self.connections) < 2 and self.active:
            if self.active:
                try:
                    print("Waiting For Data")
                    data, address = self.socket.recvfrom(2048)
                    print(data, address)

                except Exception:
                    print('Listen or Send Cancelled: Socket Most Likely Closed.')

            if address != None:
                if address not in self.connections: #If the connection is not in the list
                    self.connections.append(address)
                    print(f"Connections: {self.connections}")

            if self.active and len(self.connections) == 2:
                print("Both have connected via udp")
                self.socket.settimeout(8)
                self.handle_stream()

            else:
                if not self.active:
                    print("Drone Disconnected, Video Session Closed.")
                    break