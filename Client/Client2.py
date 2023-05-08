#Libraries
import requests
import threading
import socket
import time, copy
import numpy as np
import PySimpleGUI as sg
import subprocess


BACKEND_URL = 'http://192.168.137.187:8000/v1/api/frontend'
BACKEND_IP = '192.168.137.187'


#Something to Initialize the GUI Here

class client:
    def __init__(self) -> None:
        #-----# Initialize Variables #-----#
        self.server_info = {}
        self.active_relays = []
        self.active_drones = []

        self.connection: object = None

        self.kill_trigger = threading.Event()

        self.username = 'admin'
        self.password = '123'
        self.token = None

        self.handle()

    #-----# Main Handler #-----#
    def handle(self):
        #User Login
        self.login()

        #Create GUI
        layout = [
            [sg.Text("Select a device:")],
            [sg.Combo([], key='-ACTIVE_RELAYS-', size=(20, 1))],
            [sg.Combo([], key='-ACTIVE_DRONES-', size=(20, 1))],
            [sg.Button("Connect"), sg.Button("Exit")],
        ]

        self.window = sg.Window("Device List", layout, finalize=True)
        
        #Continuously Get Relay And Drone Info from Backend
        info_thread = threading.Thread(name='info_thread', target=self.information, args=())
        info_thread.start()


        while True:
            event, values = self.window.Read()

            if event in (sg.WIN_CLOSED, "Exit"):
                break

            if event == "Connect":
                print(f"Connecting To {values['-ACTIVE_RELAYS-']}...")

            if event == '-UPDATE_RELAYS-':
                self.window['-ACTIVE_RELAYS-'].Update(values=values[event])

            if event == '-UPDATE_DRONES-':
                self.window['-ACTIVE_DRONES-'].Update(values=values[event])

        self.window.close()


    #-----# Functions #-----#

    def user_input(self):
        #Variables
        while True:
            pass


    def login(self):
        #Get login information
        correct = False

        while correct == False:
            try:
                #Send login request
                query = {'name': self.username, 'password': self.password}
                response = requests.post(f'{BACKEND_URL}/login', json=query)

                if response.status_code != 200: #Every HTTPException.
                    if not response.json().get('access_token'):
                        print(f"Incorrect Username or Password: {response.status_code}")
                    else:
                        print(f"Server is offline | Could not connect")

                #Token information if Correct
                if response.json().get('access_token'):
                    correct = True
                    self.token = response.json().get('access_token')
            
            except Exception:
                print("Failed Connecting to Backend")
        
        print("Logged In")


    def information(self):

        old_relays = []
        old_drones = []
        while not self.kill_trigger.is_set():
            relay_list = []
            drone_list = []
            try:
                response = requests.get(f'{BACKEND_URL}/relayboxes/all')
                self.server_info = response.json()

            except Exception as e:
                print(f"{e}: Could not retrieve Relay and Drone Data")

            #Update the Relay Combo
            for relay in self.server_info.keys():
                relay_list.append(relay)

            if relay_list != old_relays:
                old_relays = relay_list
                print(relay_list)
                self.window.write_event_value('-UPDATE_RELAYS-', relay_list)

            relay = self.window['-ACTIVE_RELAYS-'].get()

            if relay in relay_list:
                for drone in self.server_info[relay]:
                    drone_list.append(drone)
            else:
                drone_list = []

            if drone_list != old_drones:
                old_drones = drone_list
                print(drone_list)
                self.window.write_event_value('-UPDATE_DRONES-', drone_list)

            time.sleep(0.2)




class controller:
    def __init__(self, port):
        #-----# Initialize Variables #-----#
        self.port = port
        self.address = ('', 8000) #Localhost
        self.backend_address = (BACKEND_IP, self.port)

        self.vidsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.vidsock.bind(self.backend_address)

        self.handle()
    
    def handle(self):
        #Send Verification Packet
        try:
            self.vidsock.sendto("rts".encode('utf-8'), self.backend_address)
        except Exception as e:
            print(f"Could not send RTS: {e}")

if __name__ == "__main__":
    control = client()