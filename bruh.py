import socket

soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

soc.bind(('', 3333))

soc.sendto(bytes('bruh', 'utf-8'), ('192.168.137.1', 52222))