import threading
import socket
import time


HOST = ''
PORT = 8889
DRONE_PORT = 11111
BACKEND_IP = '192.168.137.100' #INDSÆT IP ADDRESSE FOR MIG
BACKEND_PORT = 6969
local_address = (HOST, PORT)
backend_address = (BACKEND_IP, BACKEND_PORT)
ENCODING = 'utf-8'

#Create UDP Socket
cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Connection using IPV4
cmd_socket.bind(local_address)

vid_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
vid_socket.bind((HOST, 11111))

def recvideo():
    while True:
        try:
            data, ip = vid_socket.recvfrom(2048) #Receive vid from drone
            print(data)
            vid_socket.sendto(data, backend_address)
        except Exception as e:
            print(f'Fucked up: {e}')
            vid_socket.close()
            break

def send_control_command(command: str, buffer_size: int) -> str:
    # The port does not really matter in terms of functionallity.
    cmd_socket.sendto(bytes(command, 'utf-8'), ('192.168.137.159', 8889)) 
    status = cmd_socket.recvfrom(buffer_size)
    print(command, status)


print('Sending commands')
send_control_command('command', 2048)
time.sleep(1)
send_control_command('streamon', 2048)
time.sleep(1)
recvideo()