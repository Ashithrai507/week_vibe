import socket
import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout,
    QGridLayout, QApplication
)
from PyQt6.QtCore import Qt, QTimer

from models.device import Device
from ui.chat_window import ChatWindow

from network.discovery import DiscoveryThread

from network.tcp_server import TCPServer
from network.file_server import FileServer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyDrop")
        self.setMinimumSize(900, 600)

        # ---------- UI ----------
        central = QWidget()
        self.setCentralWidget(central)

        self.layout = QVBoxLayout(central)

        self.title = QLabel("PyDrop")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size:32px; font-weight:bold;")
        self.layout.addWidget(self.title)

        self.status = QLabel("Searching for nearby devices…")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("color: gray;")
        self.layout.addWidget(self.status)

        self.grid = QGridLayout()
        self.layout.addLayout(self.grid)

        # ---------- DATA ----------
        self.devices = {}
        self.chat_windows = {}

        # ---------- NETWORK ----------
        self.my_name = socket.gethostname()
        print("My device name:", self.my_name)

        # TCP CHAT SERVER
        self.tcp_server = TCPServer()
        self.tcp_server.message_received.connect(self.on_message_received)
        self.tcp_server.start()

        # FILE SERVER (FIXED)
        self.file_server = FileServer()
        self.file_server.start()

        # UDP DISCOVERY
        self.discovery = DiscoveryThread(self.my_name)
        self.discovery.device_found.connect(self.add_device)
        self.discovery.start()

        # UI refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_status)
        self.refresh_timer.start(2000)

    # ---------- UI HELPERS ----------
    def refresh_status(self):
        if self.devices:
            self.status.setText("Nearby devices found")
        else:
            self.status.setText("Searching for nearby devices…")

    def add_device(self, data):
        name = data.get("name")
        ip = data.get("ip")

        if not name or not ip:
            return

        if ip in self.devices:
            return

        print(f"UI adding device: {name} ({ip})")

        device = Device(name, ip, 6000)
        self.devices[ip] = device

        btn = QLabel(f"💻 {name}")
        btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn.setFixedSize(160, 120)
        btn.setStyleSheet("""
            QLabel {
                background-color: #1f1f1f;
                border-radius: 12px;
                color: white;
            }
            QLabel:hover {
                background-color: #2c2c2c;
            }
        """)
        btn.mousePressEvent = lambda e, d=device: self.open_chat(d)

        row = (len(self.devices) - 1) // 4
        col = (len(self.devices) - 1) % 4
        self.grid.addWidget(btn, row, col)



    def open_chat(self, device):
        ip = device.ip

        if ip in self.chat_windows:
            chat = self.chat_windows[ip]
            chat.show()
            chat.raise_()
            chat.activateWindow()
            return

        chat = ChatWindow(device, self)
        chat.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        chat.show()
        self.chat_windows[ip] = chat


    # ---------- MESSAGE ROUTING ----------
    def on_message_received(self, ip, message):
        device = self.devices.get(ip, Device(ip, ip, 6000))

        if ip not in self.chat_windows:
            chat = ChatWindow(device, self)
            chat.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
            chat.show()
            self.chat_windows[ip] = chat

        self.chat_windows[ip].receive(message)



    # ---------- CLEAN SHUTDOWN ----------
    def closeEvent(self, event):
        print("Closing application...")

        # ---- Stop discovery thread ----
        if hasattr(self, "discovery"):
            try:
                self.discovery.stop()
                self.discovery.terminate()
            except Exception as e:
                print("Discovery shutdown error:", e)

        # ---- Stop TCP server ----
        if hasattr(self, "tcp_server"):
            try:
                self.tcp_server.stop()
                self.tcp_server.terminate()
            except Exception as e:
                print("TCP shutdown error:", e)

        # ---- Stop File server ----
        if hasattr(self, "file_server"):
            try:
                self.file_server.stop()
                self.file_server.terminate()
            except Exception as e:
                print("File server shutdown error:", e)

        event.accept()

