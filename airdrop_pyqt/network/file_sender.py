import socket
import json
from PyQt6.QtCore import QThread
from network.constants import FILE_PORT, CHUNK_SIZE


def recv_exact(conn, size):
    data = b""
    while len(data) < size:
        part = conn.recv(size - len(data))
        if not part:
            raise ConnectionError("Connection closed")
        data += part
    return data


class FileSender(QThread):
    def __init__(self, ip, filename, save_path):
        super().__init__()
        self.ip = ip
        self.filename = filename
        self.save_path = save_path

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.ip, FILE_PORT))

        # Request file
        request = json.dumps({
            "request": self.filename
        }).encode()

        sock.sendall(len(request).to_bytes(4, "big"))
        sock.sendall(request)

        # Receive metadata
        meta_len = int.from_bytes(recv_exact(sock, 4), "big")
        meta = json.loads(recv_exact(sock, meta_len).decode())
        filesize = meta["filesize"]

        received = 0
        with open(self.save_path, "wb") as f:
            while received < filesize:
                chunk = sock.recv(min(CHUNK_SIZE, filesize - received))
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)

        sock.close()
