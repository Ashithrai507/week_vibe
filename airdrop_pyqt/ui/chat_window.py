import json
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QFileDialog
)
from PyQt6.QtCore import Qt

from network.tcp_client import SendMessageThread
from network.file_sender import FileSender
from storage.chat_db import ChatDB


class ChatWindow(QWidget):
    def __init__(self, device):
        super().__init__()
        self.device = device
        self.db = ChatDB()

        self.send_threads = []
        self.file_threads = []
        self.pending_files = {}  # filename -> Path (sender side)

        self.setWindowTitle(f"Chat – {device.name}")
        self.setMinimumSize(480, 560)

        layout = QVBoxLayout(self)

        # ---- Chat view ----
        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        self.chat_view.setOpenExternalLinks(False)
        self.chat_view.anchorClicked.connect(self.handle_link)
        self.chat_view.setStyleSheet("""
            QTextEdit {
                background-color: #121212;
                color: white;
                border: none;
                font-size: 15px;
            }
        """)

        # ---- Input ----
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a message…")
        self.input.returnPressed.connect(self.send_text)

        # ---- Buttons ----
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_text)

        file_btn = QPushButton("📎 Send File")
        file_btn.clicked.connect(self.send_file)

        layout.addWidget(self.chat_view)
        layout.addWidget(self.input)
        layout.addWidget(send_btn)
        layout.addWidget(file_btn)

        self.load_history()

    # -------------------------
    # History
    # -------------------------
    def load_history(self):
        messages = self.db.load_messages(self.device.ip)
        for direction, msg in messages:
            self.add_text_bubble(msg, direction == "sent")

    # -------------------------
    # Text messaging
    # -------------------------
    def send_text(self):
        msg = self.input.text().strip()
        if not msg:
            return

        sender = SendMessageThread(self.device.ip, msg)
        self.send_threads.append(sender)
        sender.finished.connect(lambda: self.send_threads.remove(sender))
        sender.start()

        self.db.save_message(self.device.ip, "sent", msg)
        self.add_text_bubble(msg, sent=True)
        self.input.clear()

    def receive(self, msg):
        # Try file metadata
        try:
            data = json.loads(msg)
            if data.get("type") == "file":
                self.add_file_bubble(
                    data["filename"],
                    data["filesize"],
                    sent=False
                )
                return
        except Exception:
            pass

        # Normal text
        self.db.save_message(self.device.ip, "received", msg)
        self.add_text_bubble(msg, sent=False)

    # -------------------------
    # File sending (announce only)
    # -------------------------
    def send_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select file")
        if not file_path:
            return

        path = Path(file_path)

        meta = {
            "type": "file",
            "filename": path.name,
            "filesize": path.stat().st_size
        }

        sender = SendMessageThread(self.device.ip, json.dumps(meta))
        self.send_threads.append(sender)
        sender.finished.connect(lambda: self.send_threads.remove(sender))
        sender.start()

        self.pending_files[path.name] = path
        self.add_file_bubble(path.name, path.stat().st_size, sent=True)

    # -------------------------
    # File download handling
    # -------------------------
    def handle_link(self, url):
        if url.scheme() == "download":
            filename = url.path().lstrip("/")
            self.download_file(filename)

    def download_file(self, filename):
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", filename
        )
        if not save_path:
            return

        sender = FileSender(
            self.device.ip,
            filename,
            save_path
        )
        self.file_threads.append(sender)
        sender.finished.connect(lambda: self.file_threads.remove(sender))
        sender.start()

    # -------------------------
    # UI bubbles
    # -------------------------
    def add_text_bubble(self, text, sent):
        align = "right" if sent else "left"
        color = "#1e88e5" if sent else "#2a2a2a"

        self.chat_view.append(f"""
        <div style="text-align:{align}; margin:6px;">
          <div style="
            display:inline-block;
            background:{color};
            padding:8px 12px;
            border-radius:12px;
            max-width:70%;
          ">
            {text}
          </div>
        </div>
        """)

    def add_file_bubble(self, filename, size, sent):
        align = "right" if sent else "left"
        action = "" if sent else f"""
            <a href="download:{filename}" style="color:#4fc3f7;">
                Download
            </a>
        """

        self.chat_view.append(f"""
        <div style="text-align:{align}; margin:6px;">
          <div style="
            display:inline-block;
            background:#333;
            padding:10px;
            border-radius:12px;
            max-width:70%;
          ">
            📎 <b>{filename}</b><br>
            {size // 1024} KB<br>
            {action}
          </div>
        </div>
        """)
