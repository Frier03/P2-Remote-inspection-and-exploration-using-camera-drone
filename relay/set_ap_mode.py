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

# the the first integer is the port for status the second is the video port.
udp_socket.sendto(bytes("port 8889 2003", 'utf-8'), (tello_ip, tello_port))
status2 = udp_socket.recvfrom(128)
print(status2)

"""
time.sleep(5)
udp_socket.sendto(bytes("ap LAPTOP_TEST HardwareSuperTest", 'utf-8'), (tello_ip, tello_port))
print("Set to access point mode")
status3 = udp_socket.recvfrom(128)
print(status3)
"""