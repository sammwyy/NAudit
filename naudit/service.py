class Service:
    def __init__(self, address, port, protocol, name, version):
        self.address = address
        self.port = port
        self.protocol = protocol
        self.name = name
        self.version = version

    def has_info(self):
        return self.name != "unknown" or self.version != "unknown"

    def get_full_info(self):
        if self.has_info():
            return f"{self.name} {self.version}"
        else:
            return "Unknown"

    def get_info(self):
        name = self.name
        version = self.version
        if name != "unknown":
            return name
        elif version != "unknown":
            return version
        else:
            return "unknown"

    def __str__(self):
        return f"{self.get_full_info()} {self.port}/{self.protocol}"
