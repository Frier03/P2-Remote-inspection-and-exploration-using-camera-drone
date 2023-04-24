import socket, time

host_ip = ''
host_port = 11111

tello_ip = '192.168.10.1'
tello_port = 8889

# Create UDP socket.
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

udp_socket.bind((host_ip, host_port))

# Initialize sdk and reset password
udp_socket.sendto(bytes("command", 'utf-8'), (tello_ip, tello_port))
status1 = udp_socket.recvfrom(128)
print(status1)

udp_socket.sendto(bytes("ap fakeRelay WORDPASS", 'utf-8'), (tello_ip, tello_port))
print("Set to access point mode")
status2 = udp_socket.recvfrom(128)
print(status2)