import socket
import json
import time
import platform
from PyQt6.QtCore import QThread, pyqtSignal

MCAST_GROUP = "224.1.1.1"
MCAST_PORT = 50000
INTERVAL = 2


class DiscoveryThread(QThread):
    device_found = pyqtSignal(dict)

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.running = True

    def run(self):
        recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recv_sock.bind(("", MCAST_PORT))

        mreq = socket.inet_aton(MCAST_GROUP) + socket.inet_aton("0.0.0.0")
        recv_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        recv_sock.settimeout(1)

        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        payload = json.dumps({
            "name": self.username,
            "port": 6000,
            "os": platform.system()
        }).encode()

        while self.running:
            try:
                send_sock.sendto(payload, (MCAST_GROUP, MCAST_PORT))

                try:
                    data, addr = recv_sock.recvfrom(1024)
                    info = json.loads(data.decode())

                    if info["name"] != self.username:
                        info["ip"] = addr[0]
                        self.device_found.emit(info)

                except socket.timeout:
                    pass

                time.sleep(INTERVAL)

            except Exception as e:
                print("Discovery error:", e)

        recv_sock.close()
        send_sock.close()

    def stop(self):
        self.running = False
