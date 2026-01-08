class Device:
    def __init__(self, name, ip, port):
        self.name = name
        self.ip = ip
        self.port = port

    def __repr__(self):
        return f"{self.name} ({self.ip}:{self.port})"
