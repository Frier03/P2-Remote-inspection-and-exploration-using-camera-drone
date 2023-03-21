import socket, time

host_ip = '0.0.0.0'
host_port = 11111

tello_ip = '192.168.10.1'
tello_port = 8889

backend_ip = '89.150.129.29'
backend_video_port = 6969

# Create UDP socket for sending commands and receiving the UDP stream
tello_UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_UDP_socket.bind((host_ip, host_port))

# The relay socket that sends the video to the backend server
relay_UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Initialize sdk and connect to accesspoint
tello_UDP_socket.sendto(bytes("command", 'utf-8'), (tello_ip, tello_port))
tello_UDP_socket.sendto(bytes("streamon", 'utf-8'), (tello_ip, tello_port))

while True:
    feed, source = tello_UDP_socket.recvfrom(2048)

    try:
        # Should be IP of static server
        relay_UDP_socket.sendto(bytes(feed, 'utf-8'),(backend_ip, backend_video_port))
    except Exception as error:
        print(error)
        time.sleep(1)