import socket

backend_ip = '0.0.0.0'
backend_port = 7023

backend_udp_video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
backend_udp_video_socket.bind((backend_ip, backend_port))

while True:

    relayed_feed, source = backend_udp_video_socket.recvfrom(2048)

    print(relayed_feed)
