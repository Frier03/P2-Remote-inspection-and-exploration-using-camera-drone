import PySimpleGUI as sg
import time
import threading

def get_online_devices():
    # Replace this function with your logic to get a list of online devices
    return ["Device A", "Device B", "Device C"]

def update_device_list(window, interval=2):
    while True:
        time.sleep(interval)
        online_devices = get_online_devices()
        window.write_event_value('-UPDATE_COMBO-', online_devices)

layout = [
    [sg.Text("Select a device:")],
    [sg.Combo([], key='-DEVICE_COMBO-', size=(20, 1))],
    [sg.Button("Connect"), sg.Button("Exit")],
]

window = sg.Window("Device List", layout, finalize=True)

# Start the thread to update the device list periodically
threading.Thread(target=update_device_list, args=(window,), daemon=True).start()

while True:
    event, values = window.read()

    if event in (sg.WIN_CLOSED, "Exit"):
        break
    elif event == "Connect":
        print(f"Connecting to {values['-DEVICE_COMBO-']}...")
    elif event == '-UPDATE_COMBO-':
        window['-DEVICE_COMBO-'].update(values=values[event])

window.close()