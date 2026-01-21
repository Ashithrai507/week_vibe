import socket
import json
from pathlib import Path
from PyQt6.QtCore import QThread
from network.constants import FILE_PORT, CHUNK_SIZE


class FileSender(QThread):
    def __init__(self, ip, file_path):
        super().__init__()
        self.ip = ip
        self.file_path = Path(file_path)

    def run(self):
        print(f"📤 Sending file to {self.ip}:{FILE_PORT}")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.ip, FILE_PORT))

            filesize = self.file_path.stat().st_size

            metadata = json.dumps({
                "filename": self.file_path.name,
                "filesize": filesize
            }).encode()

            sock.sendall(len(metadata).to_bytes(4, "big"))
            sock.sendall(metadata)

            with open(self.file_path, "rb") as f:
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    sock.sendall(chunk)

            sock.close()

        except Exception as e:
            print("File send error:", e)
