import socket

host_ip = ''
host_port = 11111

tello_ip = '192.168.137.112'
tello_port = 8889

# Create UDP socket.
video_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

video_udp_socket.bind((host_ip, host_port))

# Initialize sdk 
video_udp_socket.sendto(bytes("command", 'utf-8'), (tello_ip, tello_port))
video_udp_socket.sendto(bytes("streamon", 'utf-8'), (tello_ip, tello_port))

print('Done')

while True:
    response, ip = video_udp_socket.recvfrom(2048)

    print(response)