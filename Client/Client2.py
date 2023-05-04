import socket
from time import sleep
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt
import sys

global response_socket

response_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
response_socket.bind(('', 8889))
response_socket.settimeout(2)

def send_control_command(command: str, buffer_size: int) -> bool|None:
    tello_ip = '192.168.137.65'

    while True:
        try:

            response = None
            addr = None

            try:
                # Send command and await response.
                print(f'Sending command: {command} to drone')
                response_socket.sendto(bytes(command, 'utf-8'), (tello_ip, 8889)) 
                response, addr = response_socket.recvfrom(buffer_size)

            except OSError:
                sleep(2)

            if response != None:
                decoded_response = response.decode('utf-8')

                if ('ok' == decoded_response):
                    return True

        except Exception as socket_error:
            print(f'Error: {socket_error}')


send_control_command('command', 2048)
send_control_command('streamon', 2048)

class VideoWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Live Video')

        # Set up layout
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Create a container QWidget for the FFmpeg video player
        container = QWidget(self)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        container.setAttribute(Qt.WA_NativeWindow, True)
        layout.addWidget(container)

        # FFmpeg command and arguments
        args = ['C:/Users/srisb/source/repos/P2/ffmpeg-master-latest-win64-gpl/ffmpeg-master-latest-win64-gpl/bin/ffplay',
                '-i', 'udp://0.0.0.0:11111',
                '-probesize', '32',
                '-framerate', '30',
                '-fflags', 'nobuffer',
                '-flags', 'low_delay',
                '-framedrop',
                '-strict', 'experimental',
                '-an',  # Disable audio
                '-sn',  # Disable subtitles
                '-window_title', 'video',  # Set window title
                '-noborder',  # No window border
                ]

        # Start FFmpeg as a subprocess
        self.process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)

        # Embed FFmpeg window in the container QWidget
        winId = int(self.process.stdout.readline())
        container.createWindowContainer(container.window().fromWinId(winId), container)

        # Clean up when the application is closed
        self.setAttribute(Qt.WA_DeleteOnClose, True)

    def closeEvent(self, event):
        self.process.stdin.write(b'q')
        self.process.stdin.flush()
        self.process.wait()

# Create a PyQt5 application and display the video
app = QApplication(sys.argv)
window = VideoWindow()
window.show()
sys.exit(app.exec_())