import socket

host_ip = ''
host_port = 11111

tello_ip = '192.168.10.1'
tello_port = 8889

# Create UDP socket.
video_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

video_udp_socket.bind((host_ip, host_port))

# Initialize sdk and reset password
video_udp_socket.sendto(bytes("command", 'utf-8'), (tello_ip, tello_port))
video_udp_socket.sendto(bytes("ap LAPTOP_TEST HardwareSuperTest", 'utf-8'), (tello_ip, tello_port))
