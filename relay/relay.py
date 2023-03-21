#This will allow sending commands and receiving videofeed
import threading
import socket
import time
#import cv2
import keyboard

HOST = ''
PORT = 9000
TELLOPORT = 8889
local_address = (HOST, PORT)
tello_address = ('192.168.10.1', 8889)
backend_address = ('89.150.129.29', 6969)
ENCODING = 'utf-8'

altitude = 20

#Create UDP Socket
cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP Connection using IPV4

cmd_socket.bind(local_address)

def sendmsg(msg):
    msg = msg.encode(encoding="utf-8")
    sent = cmd_socket.sendto(msg, tello_address)


def recv():
    while True:
        try:
            data, server = cmd_socket.recvfrom(2048)
            print(f"{data.decode(encoding=ENCODING)} from {server}")
        except Exception:
            print('\nExit . . .\n')
            break


def recvideo():
    #Tell the Tello to enable video stream
    print("streamon")
    cmd_socket.sendto("streamon".encode(encoding="utf-8"), tello_address)

    vidsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #New Socket to receive Video Data
    vidsock.bind(('', 11111)) #Bind the socket to the listening port

    #cap = cv2.VideoCapture('udp://@0.0.0.0:11111') #Create an OpenCV video Capture object

    while True:
        try:
            vid, server = vidsock.recvfrom(2048) #Receive Video Data from the drone
            cmd_socket.sendto(vid, backend_address) #Send the Data to the backend_address server

        except KeyboardInterrupt:
            break

#recvThread Createq
recvThread = threading.Thread(target=recv, daemon=True)
recvThread.start()

#Enable Video Stream and Start Receiving
print("Enabling SDK Mode")
cmd_socket.sendto("command".encode(encoding="utf-8"), tello_address)

#videoThread = threading.Thread(target=recvideo, daemon=True)
#videoThread.start()


while True: 
    try:
        if keyboard.is_pressed("a"):
            sendmsg("left 20")
            print("left 20")
            time.sleep(0.8)

        if keyboard.is_pressed("d"):
            sendmsg("right 20")
            print("right 20")
            time.sleep(0.8)

        if keyboard.is_pressed("s"):
            sendmsg("back 20")
            print("back 20")
            time.sleep(0.8)

        if keyboard.is_pressed("w"):
            sendmsg("forward 20")
            print("forward 20")
            time.sleep(0.8)

        if keyboard.is_pressed("space"):
            altitude += 10
            sendmsg("up 20")
            print("up 20")
            time.sleep(0.8)

        if keyboard.is_pressed("shift"):
            altitude -= 10
            sendmsg("down 20")
            print("down 20")
            time.sleep(0.8)

        if keyboard.is_pressed("t"):
            sendmsg("takeoff")
            print("takeoff")
            time.sleep(0.8)

        if keyboard.is_pressed("l"):
            sendmsg("land")
            print("Land")
            time.sleep(0.8)

        if keyboard.is_pressed("q"):
            sendmsg("emergency")
            print("Emergency")
            time.sleep(0.8)

    except KeyboardInterrupt:
        print ('\n . . .\n')
        cmd_socket.close()
        break

    '''
        #cap = cv2.VideoCapture('udp://@0.0.0.0:11111') #Create an OpenCV video Capture object

    while True:
        try:
            vid, server = sock.recvfrom(2048, )
            # Read a frame from the video stream
            #ret, frame = cap.read()

            #Display the frame in a window
            #cv2.imshow('Tello EDU Stream', frame)

            #Wait for a key press and check if the 'q' key was pressed
            #if cv2.waitKey(1) & 0xFF == ord('q'):
                #break

        except KeyboardInterrupt:
            break

    #cap.release()
    #cv2.destroyAllWindows()
    '''