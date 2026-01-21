import socket
import json
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal
from network.constants import FILE_PORT, CHUNK_SIZE


class FileServer(QThread):
    file_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # ✅ VERY IMPORTANT: allow reuse
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server.bind(("0.0.0.0", FILE_PORT))
        server.listen(1)

        print("📂 File server listening on port", FILE_PORT)
        conn, addr = server.accept()
        print("📥 Incoming file connection from", addr)

        while self.running:
            try:
                conn, addr = server.accept()

                # ---- receive metadata ----
                meta_len = int.from_bytes(conn.recv(4), "big")
                meta = json.loads(conn.recv(meta_len).decode())

                filename = meta["filename"]
                filesize = meta["filesize"]

                download_dir = Path.home() / "Downloads" / "PyDrop"
                download_dir.mkdir(parents=True, exist_ok=True)

                filepath = download_dir / filename

                with open(filepath, "wb") as f:
                    received = 0
                    while received < filesize:
                        data = conn.recv(CHUNK_SIZE)
                        if not data:
                            break
                        f.write(data)
                        received += len(data)

                conn.close()
                self.file_received.emit(filename)

            except Exception as e:
                if self.running:
                    print("File receive error:", e)

        server.close()

    def stop(self):
        self.running = False
