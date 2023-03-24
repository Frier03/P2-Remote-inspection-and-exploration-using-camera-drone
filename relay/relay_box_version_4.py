import socket
from threading import Thread

class relay_box():
    def __init__(self):
        1+1
        

ENCODING = 'utf-8'

# The ip and specific listening port of the backend server.
backend_server_ip = '123.123.123.123'
backend_server_session_port = 5000

host_ip = ''
host_port = 11111
 

# Tello stationmode ip, !!! on specific network !!!
tello_ip = '192.168.137.1'
tello_port = 8889
tello_addr = (tello_ip, tello_port)

# Create UDP video feed socket.
tello_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_udp_socket.bind((host_ip, host_port))

# Initialize sdk 
tello_udp_socket.sendto(bytes('command', ENCODING), tello_addr)
tello_udp_socket.sendto(bytes('streamon', ENCODING), tello_addr)


# Create TCP handshake socket.
session_port_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
session_port_socket.connect((backend_server_ip, backend_server_session_port))


def process_drone_feed(backend_server_ip, backend_server_udp_port):

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_addr = (backend_server_ip, backend_server_udp_port)

    # Should be while true, range is only for testing !!!!!!!!!!!!!
    for i in range(100):
        feed, addr = tello_udp_socket.recvfrom(2048)

        udp_socket.send((feed, ENCODING), udp_addr)


def get_session_ports():

    secret_key = 'SkdLApr229,.WWDsj-iT'

    # Send secret key to backend to authenticate drone.
    session_port_socket.send((secret_key, ENCODING))

    # Receive new communication ports for TCP and UDP from backend.
    data, addr = session_port_socket.recv(64)
    decoded_data = data.decode(ENCODING)

    session_ports = decoded_data.split(',')

    print(session_ports)

    return session_ports


def process_client_commands(backend_server_ip, backend_server_tcp_port):

    command = None

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_addr = (backend_server_ip, backend_server_tcp_port)
    tcp_socket.connect(tcp_addr)

    while command != 'close_connection':
        while True:
            command, addr = tcp_socket.recv(128)
            
            if not command or command == 'close_connection':
                break

            tello_udp_socket.sendto(bytes(command, ENCODING), tello_addr)

            command = None


# run ---------------------------------------

session_ports = get_session_ports()

tcp_command_thread = Thread(target=process_client_commands, args=(backend_server_ip, session_ports[0]), daemon=True)
tcp_command_thread.start()

video_feed_thread = Thread(target=process_drone_feed, args=(tello_addr, backend_server_ip, session_ports[1]), daemon=True)
video_feed_thread.start()

