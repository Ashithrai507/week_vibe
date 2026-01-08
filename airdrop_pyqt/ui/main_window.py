import socket
import platform

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QLabel,
    QVBoxLayout, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt

from network.file_server import FileServer
from network.discovery import DiscoveryThread
from network.tcp_server import TCPServer
from models.device import Device
from ui.chat_window import ChatWindow


# ---------------- Device Tile ---------------- #
class DeviceTile(QFrame):
    def __init__(self, device, on_click):
        super().__init__()
        self.device = device
        self.on_click = on_click
        self.file_server = FileServer()
        self.file_server.start()

        self.setFixedSize(140, 140)
        self.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 14px;
            }
            QFrame:hover {
                background-color: #2a2a2a;
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("💻")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 36px;")

        name = QLabel(device.name)
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name.setStyleSheet("color: white;")

        layout.addWidget(icon)
        layout.addWidget(name)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        self.on_click(self.device)


# ---------------- Main Window ---------------- #
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyDrop")
        self.setMinimumSize(900, 600)
        self.setStyleSheet("background-color: #121212;")

        # UNIQUE DEVICE NAME (CRITICAL)
        self.device_name = f"{socket.gethostname()}-{platform.system()}"
        print("My device name:", self.device_name)

        self.devices = {}        # ip -> Device
        self.tiles = {}          # ip -> DeviceTile
        self.chat_windows = {}   # ip -> ChatWindow

        # -------- UI -------- #
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        title = QLabel("PyDrop")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; color: white;")

        self.status = QLabel("Searching for nearby devices…")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("color: #aaaaaa;")

        self.grid = QGridLayout()
        self.grid.setSpacing(20)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)

        main_layout.addWidget(title)
        main_layout.addWidget(self.status)
        main_layout.addLayout(self.grid)

        central.setLayout(main_layout)

        # -------- Discovery -------- #
        self.discovery = DiscoveryThread(self.device_name)
        self.discovery.device_found.connect(self.add_device)
        self.discovery.start()

        # -------- TCP Server -------- #
        self.tcp_server = TCPServer()
        self.tcp_server.message_received.connect(self.on_message_received)
        self.tcp_server.start()

    # ---------------- Add Device ---------------- #
    def add_device(self, info):
        ip = info["ip"]

        if ip in self.devices:
            return

        device = Device(info["name"], ip, info["port"])
        print("UI adding device:", device)

        tile = DeviceTile(device, self.open_chat)

        index = len(self.devices)
        row = index // 4
        col = index % 4

        self.grid.addWidget(tile, row, col)

        self.devices[ip] = device
        self.tiles[ip] = tile

        self.status.setText("Nearby devices found")

    # ---------------- Open Chat ---------------- #
    def open_chat(self, device):
        if device.ip in self.chat_windows:
            chat = self.chat_windows[device.ip]
            if chat.isVisible():
                chat.raise_()
                chat.activateWindow()
                return

        chat = ChatWindow(device)
        chat.destroyed.connect(lambda: self.chat_windows.pop(device.ip, None))
        self.chat_windows[device.ip] = chat
        chat.show()


    # ---------------- Receive Message ---------------- #
    def on_message_received(self, ip, message):
        if ip not in self.chat_windows and ip in self.devices:
            self.open_chat(self.devices[ip])

        if ip in self.chat_windows:
            self.chat_windows[ip].receive(message)

    # ---------------- Close Cleanly ---------------- #
    def closeEvent(self, event):
        print("Closing application...")

        self.discovery.stop()
        self.discovery.terminate()

        self.tcp_server.stop()
        self.tcp_server.terminate()
        self.file_server.stop()
        self.file_server.terminate()

        event.accept()
