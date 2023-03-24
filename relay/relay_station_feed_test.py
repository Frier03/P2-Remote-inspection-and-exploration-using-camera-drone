import socket

ENCODING = 'utf-8'

# The ip and specific listening port of the backend server.
backend_server_ip = '123.123.123.123'
backend_server_port = 5000

host_ip = ''
host_port = 11111

# Tello stationmode ip, !!! on specific network !!!
tello_ip = '192.168.137.1'
tello_port = 8889

# Create UDP socket.
video_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
video_udp_socket.bind((host_ip, host_port))

# Create TCP handshake socket.
session_port_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
session_port_socket.connect((backend_server_ip, backend_server_port))

# Initialize sdk 
video_udp_socket.sendto(bytes('command', ENCODING), (tello_ip, tello_port))
video_udp_socket.sendto(bytes('streamon', ENCODING), (tello_ip, tello_port))

def get_drone_feed():
    while True:
        feed, addr = video_udp_socket.recvfrom(2048)

        print(feed)

def get_session_ports():

    secret_key = 'SkdLApr229,.WWDsj-iT'

    # Send secret key to backend to authenticate drone.
    session_port_socket.send((secret_key, ENCODING))

    # Receive new communication ports for TCP and UDP from backend.
    data, addr = session_port_socket.recv(64)
    session_ports = data.decode(ENCODING)

    print(session_ports, addr)


get_session_ports()