import socket
from threading import Thread

class relay_box():
    def __init__(self, host_port = 11111, tello_ip='192.168.137.1', backend_server_ip = '123.123.123.123'):
        
        self.ENCODING = 'utf-8'
        self.command = None

        # The ip and specific listening port of the backend server.
        self.backend_server_ip = backend_server_ip
        self.backend_server_session_port = 5000

        self.host_ip = ''
        self.host_port = host_port
        
        # Tello stationmode ip, !!! on specific network !!!
        self.tello_ip = tello_ip
        self.tello_port = 8889
        self.tello_addr = (self.tello_ip, self.tello_port)

        # Create UDP video feed socket.
        self.tello_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tello_udp_socket.bind((self.host_ip, self.host_port))

        # Initialize sdk 
        self.tello_udp_socket.sendto(bytes('command', self.ENCODING), self.tello_addr)
        self.tello_udp_socket.sendto(bytes('streamon', self.ENCODING), self.tello_addr)

        # Create TCP handshake socket.
        self.session_port_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.session_port_socket.connect((self.backend_server_ip, self.backend_server_session_port))
                
        session_ports = relay_box.get_session_ports()

        self.backend_server_udp_port = session_ports[1]
        self.backend_server_tcp_port = session_ports[0]


    def process_drone_feed(self):

        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_addr = (self.backend_server_ip, self.backend_server_udp_port)

        # Should be while true, range is only for testing !!!!!!!!!!!!!
        for i in range(100):
            feed, addr = self.tello_udp_socket.recvfrom(2048)

            udp_socket.send((feed, self.ENCODING), udp_addr)


    def get_session_ports(self):

        secret_key = 'SkdLApr229,.WWDsj-iT'

        # Send secret key to backend to authenticate drone.
        self.session_port_socket.send((secret_key, self.ENCODING))

        # Receive new communication ports for TCP and UDP from backend.
        data, addr = self.session_port_socket.recv(64)
        decoded_data = data.decode(self.ENCODING)

        session_ports = decoded_data.split(',')

        print(session_ports)

        return session_ports


    def process_client_commands(self):

        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_addr = (self.backend_server_ip, self.backend_server_tcp_port)
        tcp_socket.connect(tcp_addr)

        while self.command != 'close_connection':
            while True:
                command, addr = tcp_socket.recv(128)
                
                if not command or command == 'close_connection':
                    break

                self.tello_udp_socket.sendto(bytes(command, self.ENCODING), self.tello_addr)

                command = None

    
    def start_tcp_command_thread(self):
        tcp_command_thread = Thread(target=relay_box.process_client_commands, args=(self), daemon=True)
        tcp_command_thread.start()


    def start_video_feed_thread(self):
        video_feed_thread = Thread(target=relay_box.process_drone_feed, args=(self), daemon=True)
        video_feed_thread.start()



test = relay_box()

test.start_tcp_command_thread()
test.start_video_feed_thread()

print('h')

