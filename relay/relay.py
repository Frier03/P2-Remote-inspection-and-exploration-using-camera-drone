import socket

host_ip = '0.0.0.0'
host_port = 11111

tello_ip = '192.168.10.1'
tello_port = 8889

# Create UDP socket 
relay_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

relay_udp_socket.bind((host_ip, host_port))

# Initialize sdk and connect to accesspoint
relay_udp_socket.sendto(bytes("command", 'utf-8'), (tello_ip, tello_port))
relay_udp_socket.sendto(bytes("streamon", 'utf-8'), (tello_ip, tello_port))

while True:
    feed, source = relay_udp_socket.recvfrom(2048)



    # Should be IP of static server
    relay_udp_socket.sendto(feed,('127.0.0.1', 7023))