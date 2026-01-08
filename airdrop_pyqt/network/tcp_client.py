import socket
from PyQt6.QtCore import QThread

TCP_PORT = 6000


class SendMessageThread(QThread):
    def __init__(self, ip, message):
        super().__init__()
        self.ip = ip
        self.message = message

    def run(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((self.ip, TCP_PORT))
            sock.sendall(self.message.encode())
            sock.close()
        except Exception as e:
            print("Send failed:", e)
