from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit,
    QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog
from network.file_sender import FileSender

from network.tcp_client import SendMessageThread
from storage.chat_db import ChatDB


class ChatWindow(QWidget):
    def __init__(self, device):
        super().__init__()
        self.device = device

        self.db = ChatDB()
        self.send_threads = []

        self.setWindowTitle(f"Chat – {device.name}")
        self.setMinimumSize(460, 560)

        layout = QVBoxLayout()

        # Chat view
        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        self.chat_view.setStyleSheet("""
            QTextEdit {
                background-color: #121212;
                color: white;
                border: none;
                font-size: 16px;
            }
        """)

        # Input
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a message…")
        self.input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 15px;
            }
        """)
        self.input.returnPressed.connect(self.send)

        # Send button
        send_btn = QPushButton("Send")
        send_btn.setStyleSheet("""
            QPushButton {
                padding: 12px;
                font-size: 15px;
                background-color: #1e88e5;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        send_btn.clicked.connect(self.send)
        file_btn = QPushButton("📎 Send File")
        file_btn.clicked.connect(self.send_file)
        layout.addWidget(file_btn)


        layout.addWidget(self.chat_view)
        layout.addWidget(self.input)
        layout.addWidget(send_btn)
        self.setLayout(layout)

        # Load chat history
        self.load_history()

    # ---------- Load stored messages ----------
    def load_history(self):
        messages = self.db.load_messages(self.device.ip)
        for direction, msg in messages:
            self.add_bubble(msg, direction)

    # ---------- Message bubble (TABLE BASED) ----------
    def add_bubble(self, message, direction):
        if direction == "sent":
            html = f"""
            <table width="100%" cellspacing="0" cellpadding="4">
              <tr>
                <td></td>
                <td align="right">
                  <div style="
                    background:#1e88e5;
                    color:white;
                    padding:10px 14px;
                    border-radius:14px;
                    max-width:260px;
                    font-size:16px;
                  ">
                    {message}
                  </div>
                </td>
              </tr>
            </table>
            """
        else:
            html = f"""
            <table width="100%" cellspacing="0" cellpadding="4">
              <tr>
                <td align="left">
                  <div style="
                    background:#2a2a2a;
                    color:white;
                    padding:10px 14px;
                    border-radius:14px;
                    max-width:260px;
                    font-size:16px;
                  ">
                    {message}
                  </div>
                </td>
                <td></td>
              </tr>
            </table>
            """

        self.chat_view.append(html)
        self.chat_view.verticalScrollBar().setValue(
            self.chat_view.verticalScrollBar().maximum()
        )

    # ---------- Send ----------
    def send(self):
        msg = self.input.text().strip()
        if not msg:
            return

        sender = SendMessageThread(self.device.ip, msg)
        self.send_threads.append(sender)
        sender.finished.connect(lambda: self.send_threads.remove(sender))
        sender.start()

        self.db.save_message(self.device.ip, "sent", msg)
        self.add_bubble(msg, "sent")
        self.input.clear()

    def send_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select file")
        if not file_path:
            return

        sender = FileSender(self.device.ip, file_path)
        sender.start()

        self.chat_view.append(
            f"<i>📎 Sent file: {Path(file_path).name}</i>"
        )


    # ---------- Receive ----------
    def receive(self, msg):
        self.db.save_message(self.device.ip, "received", msg)
        self.add_bubble(msg, "received")
