import subprocess, requests, socket, threading, PySimpleGUI as sg
from time import sleep


BACKEND_URL = 'http://localhost:8000/v1/api/frontend'
BACKEND_IP = ''


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

        self.video_port = None

        self.ffmpeg_cmd = ['C:/Users/srisb/source/repos/P2/ffmpeg-master-latest-win64-gpl/ffmpeg-master-latest-win64-gpl/bin/ffplay',
                            '-i', f'udp://0.0.0.0:{self.video_port}',
                            '-probesize', '32',
                            '-framerate', '30',
                            '-fflags', 'nobuffer',
                            '-flags', 'low_delay',
                            '-framedrop',
                            '-strict', 'experimental']

        self.handle()

    #-----# Main Handler #-----#
    def handle(self):
        #User Login
        self.login()

        #Create GUI
        layout = [
            [sg.Text('Select a device:')],
            [sg.Combo([], key='-combo.active_relays-', size=(20, 1), readonly=True)],
            [sg.Combo([], key='-combo.active_drones-', size=(20, 1), readonly=True)],
            [sg.Button(button_text='Connect', key='-button.connect_drone-'), sg.Button(button_text='Disconnect', key='-button.disconnect_drone-', disabled=True)], 
            [sg.Button(button_text='Exit Program', key='-button.exit_program-')],
            ]

        self.window = sg.Window('Device List', layout, finalize=True)
        
        #Continuously Get Relay And Drone Info from Backend
        info_thread = threading.Thread(name='info_thread', target=self.information, args=())
        info_thread.start()


        while True:
            event, values = self.window.Read()

            if event in (sg.WIN_CLOSED, '-button.exit_program-'):
                try:
                    process.kill()
                    print('ffmpeg process killed')
                except:
                    print('ffmpeg process was never begun...')
                
                # Kill the information gathering thread
                self.kill_trigger.set()
                break

            if event == '-button.connect_drone-':
                
                if (self.window['-combo.active_relays-'].get() != '') and (self.window['-combo.active_drones-'].get() != ''):

                    # Get specific drone json from dict
                    connected_drone_info = self.server_info[self.window['-combo.active_relays-'].get()][self.window['-combo.active_drones-'].get()]

                    self.window['-button.connect_drone-'].Update(disabled=True)
                    self.window['-button.disconnect_drone-'].Update(disabled=False)

                    self.video_port = int(connected_drone_info['port'])

                    process = subprocess.Popen(self.ffmpeg_cmd, stdout=subprocess.PIPE)

            if event == '-button.disconnect_drone-':

                self.window['-button.connect_drone-'].Update(disabled=False)
                self.window['-button.disconnect_drone-'].Update(disabled=True)

                try:
                    process.kill()
                    print('ffmpeg process killed')
                except:
                    print('ffmpeg process was never begun...')

            if event == '-UPDATE_RELAYS-':
                self.window['-combo.active_relays-'].Update(values=values[event])

            if event == '-UPDATE_DRONES-':
                self.window['-combo.active_drones-'].Update(values=values[event])


        self.window.close()


    def user_input(self):
        #Variables
        while True:
            pass


    def login(self):
        #Get login information
        correct_login = False

        while correct_login == False:
            try:
                #Send login request
                query = {'name': self.username, 'password': self.password}
                response = requests.post(f'{BACKEND_URL}/login', json=query)

                if response.status_code != 200: #Every HTTPException.
                    if not response.json().get('access_token'):
                        print(f'Incorrect Username or Password: {response.status_code}')
                    else:
                        print(f'Server is offline | Could not connect')

                #Token information if Correct
                if response.json().get('access_token'):
                    correct_login = True
                    self.token = response.json().get('access_token')
            
            except Exception:
                print('Failed Connecting to Backend')
        
        print(f'<{self.username}> logged on')


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
                print(f'{e}: Could not retrieve Relay and Drone Data')
            
            try:
                #Update the Relay Combo
                for relay in self.server_info.keys():
                    relay_list.append(relay)

                if relay_list != old_relays:
                    old_relays = relay_list
                    self.window.write_event_value('-UPDATE_RELAYS-', relay_list)

                relay = self.window['-combo.active_relays-'].get()

                if relay in relay_list:
                    for drone in self.server_info[relay]:
                        drone_list.append(drone)
                else:
                    drone_list = []

                if drone_list != old_drones:
                    old_drones = drone_list
                    self.window.write_event_value('-UPDATE_DRONES-', drone_list)

                sleep(0.2)

            except AttributeError as tk:
                print('Error failed to update drone and or relay since the gui have been killed.')
        
        print('finished loop')

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
            self.vidsock.sendto('rts'.encode('utf-8'), self.backend_address)
        except Exception as e:
            print(f'Could not send RTS: {e}')


if __name__ == '__main__':
    control = client()