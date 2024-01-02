import subprocess

from file_utils import get_path
from loggable import Loggable
from service import Service

class Scanner(Loggable):
    def __init__(self, target):
        self.target = target
        self.ttl = -1
        self.tcp_ports = []

    def scan_ports(self):
        output = get_path("ports.xml")
        cmd = ["nmap", "-p-", "--open", "--min-rate", "5000", "-sS", "-n", "-Pn", "-vvv", self.target, '-oX', output]
        proc = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

        while proc.poll() is None:
            line = proc.stdout.readline().strip()
            if "Discovered open port" in line:
                raw_port = line.split()[3]
                port = int(raw_port.split("/")[0])
                protocol = raw_port.split("/")[1]
                if protocol == "tcp":
                    self.tcp_ports.append(port)
                super().info(f"* Found open port {port} ({protocol})")
            elif "You requested a scan type which requires root privileges" in line:
                super().error("* You need to run this script as root.")
                return False
            elif "ttl" in line:
                raw_ttl = line.split()[5]
                self.ttl = int(raw_ttl)

        return True

    def scan_service(self, port):
        output = get_path("services.xml")
        cmd = ["nmap", "-p", str(port), "-sVC", "-n", "-Pn", self.target, '-oX', output]
        proc = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        service = None

        while proc.poll() is None:
            line = proc.stdout.readline().strip()
            if "open" in line and ("/tcp" in line or "/udp" in line):
                parts = line.split()
                raw_port = parts[0]
                port = int(raw_port.split("/")[0])
                protocol = raw_port.split("/")[1]
                service = parts[2]
                version = "unknown"
                if len(parts) > 3:
                    rest = parts[3:]
                    version = " ".join(rest)

                super().ok(f"* Discovered service {port}/{protocol} - {service} | {version}")
                service = Service(self.target, port, protocol, service, version)
            elif "You requested a scan type which requires root privileges" in line:
                super().error("* You need to run this script as root.")
                return None

        return service

    def scan_services(self):
        services = []

        for port in self.tcp_ports:
            service = self.scan_service(port)
            if service is not None:
                services.append(service)
            else:
                return None

        return services

    def __str__(self) -> str:
        return "Scanner"
