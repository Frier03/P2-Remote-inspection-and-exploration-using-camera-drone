import cv2
import socket
import threading
import numpy as np
from pynput import keyboard


HOST = ''
PORT = 9000
ENCODING = 'utf-8'
local_address = (HOST, PORT)

#Tello drone IP and port
tello_address = ('192.168.137.151', 8889)

#Backend Server
backend_address = ('89.150.129.29', 6969)

#Create UDP Socket
cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Connection using IPV4
cmd_socket.bind(local_address)

def send_command(command):
    try:
        cmd_socket.sendto(command.encode(ENCODING), tello_address)
    except Exception as e:
        print(f"Error Sending Command: {e}")

# Send commands to Tello drone
send_command('command')  # Initialize SDK mode
send_command('port 8889 2003')

def receive_response():
    while True:
        try:
            response, ip = cmd_socket.recvfrom(1024)
            print(f"{response.decode(encoding=ENCODING)} from {ip}")
        except Exception as e:
            print(f"Error receiving response: {e}")
            break

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

# Create threads for receiving response and video
response_thread = threading.Thread(target=receive_response)
video_thread = threading.Thread(target=video_receiver)

response_thread.start()
video_thread.start()


send_command('streamon')  # Start video stream

def on_press(key):
    #Temp Flight Data
    altitude = 50
    try:
        if key.char == 't':
            1+1
            #send_command('takeoff')
        elif key.char == 'l':
            send_command('land')
        elif key.char == 'w':
            send_command('forward 50')
        elif key.char == 's':
            send_command('back 50')
        elif key.char == 'a':
            send_command('left 50')
        elif key.char == 'd':
            send_command('right 50')
        elif key.char == 'q':
            send_command('ccw 20')
        elif key.char == 'e':
            send_command('cw 20')
        elif key.char == 'm':
            send_command('emergency')
        elif key.char == 'x':
            altitude += 10
            send_command(f'up {altitude}')
        elif key.char == 'z':
            altitude -= 10
            send_command(f'down {altitude}')
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:
        return False

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    print("Press 'v' in the video window to stop the stream and exit.")
    video_thread.join()
    listener.join()

send_command('streamoff')  # Stop video stream
send_command('land')  # Land the drone

cmd_socket.close()