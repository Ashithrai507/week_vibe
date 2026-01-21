import socket
import json
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal
from network.constants import FILE_PORT, CHUNK_SIZE


def recv_exact(conn, size):
    data = b""
    while len(data) < size:
        packet = conn.recv(size - len(data))
        if not packet:
            raise ConnectionError("Connection closed during recv")
        data += packet
    return data


class FileServer(QThread):
    file_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", FILE_PORT))
        server.listen(5)

        print("📂 File server listening on port", FILE_PORT)

        while self.running:
            try:
                conn, addr = server.accept()
                print("📥 Incoming file connection from", addr)

                # ---- RECEIVE METADATA SAFELY ----
                meta_len_bytes = recv_exact(conn, 4)
                meta_len = int.from_bytes(meta_len_bytes, "big")

                meta_bytes = recv_exact(conn, meta_len)
                meta = json.loads(meta_bytes.decode())

                filename = meta["filename"]
                filesize = meta["filesize"]

                download_dir = Path.home() / "Downloads" / "PyDrop"
                download_dir.mkdir(parents=True, exist_ok=True)

                filepath = download_dir / filename

                print(f"📥 Receiving file {filename} ({filesize} bytes)")

                received = 0
                with open(filepath, "wb") as f:
                    while received < filesize:
                        chunk = conn.recv(min(CHUNK_SIZE, filesize - received))
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)

                conn.close()

                print("✅ File saved to", filepath)
                self.file_received.emit(filename)

            except Exception as e:
                if self.running:
                    print("❌ File receive error:", e)

        server.close()

    def stop(self):
        self.running = False
