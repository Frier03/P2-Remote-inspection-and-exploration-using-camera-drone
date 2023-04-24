import socket, cv2

host_ip = '0.0.0.0'
host_port = 2003

tello_ip = '192.168.137.161'
tello_port = 8889

# Create UDP socket
relay_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

relay_udp_socket.bind((host_ip, host_port))

# Initialize sdk and connect to accesspoint
relay_udp_socket.sendto(bytes("command", 'utf-8'), (tello_ip, tello_port))
relay_udp_socket.sendto(bytes("port 8889 2003", 'utf-8'), (tello_ip, tello_port))
relay_udp_socket.sendto(bytes("streamon", 'utf-8'), (tello_ip, tello_port))


def video_receiver():
    #Create Capture Object
    cap = cv2.VideoCapture('udp://0.0.0.0:2003')

    while True:
        #Read a frame from the video stream
        ret, frame = cap.read()

        #Was Frame read correctly
        if not ret:
            break

        #Display the frame
        cv2.imshow('Tello Video Stream', frame)

        #Close the video Stream
        key = cv2.waitKey(1) & 0xFF
        if key == ord('v'):
            break

    cap.release()
    cv2.destroyAllWindows()

video_receiver()