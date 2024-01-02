class Service:
    def __init__(self, address, port, protocol, name, version):
        self.address = address
        self.port = port
        self.protocol = protocol
        self.name = name
        self.version = version

    def __str__(self):
        return f'{self.protocol}://{self.address}:{self.port} ({self.name}) ({self.version})'
