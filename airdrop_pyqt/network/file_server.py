import socket
import json
from pathlib import Path
from PyQt6.QtCore import QThread
from network.constants import FILE_PORT, CHUNK_SIZE


def recv_exact(conn, size):
    data = b""
    while len(data) < size:
        chunk = conn.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Connection closed")
        data += chunk
    return data


class FileServer(QThread):
    def __init__(self):
        super().__init__()
        self.running = True

        # Files that THIS device can serve
        self.shared_files = {}  # filename -> Path

    def add_file(self, path: Path):
        self.shared_files[path.name] = path

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", FILE_PORT))
        server.listen(5)

        print("📂 File server listening on port", FILE_PORT)

        while self.running:
            try:
                conn, addr = server.accept()
                print("📥 Incoming file request from", addr)

                # ---- receive request ----
                req_len = int.from_bytes(recv_exact(conn, 4), "big")
                request = json.loads(recv_exact(conn, req_len).decode())

                filename = request.get("request")
                if not filename or filename not in self.shared_files:
                    print("❌ Requested file not found:", filename)
                    conn.close()
                    continue

                path = self.shared_files[filename]
                filesize = path.stat().st_size

                # ---- send metadata ----
                meta = json.dumps({
                    "filename": filename,
                    "filesize": filesize
                }).encode()

                conn.sendall(len(meta).to_bytes(4, "big"))
                conn.sendall(meta)

                # ---- send file ----
                with open(path, "rb") as f:
                    while chunk := f.read(CHUNK_SIZE):
                        conn.sendall(chunk)

                print("✅ File sent:", filename)
                conn.close()

            except Exception as e:
                if self.running:
                    print("❌ File server error:", e)

        server.close()

    def stop(self):
        self.running = False
