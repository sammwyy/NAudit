import json
import subprocess

from colorama import Fore
from file_utils import get_path
from loggable import Loggable
from service import Service

class Scanner(Loggable):
    def __init__(self, target):
        self.target = target
        self.ttl = -1
        self.services = []
        self.exploits = []

    def is_windows(self):
        return self.ttl == 129 or self.ttl == 128 or self.ttl == 127

    def is_unix(self):
        return self.ttl == 65 or self.ttl == 64 or self.ttl == 63

    def is_solaris(self):
        return self.ttl == 255 or self.ttl == 254 or self.ttl == 253

    def get_os(self):
        if self.is_windows():
            return "Windows"
        elif self.is_unix():
            return "Unix"
        elif self.is_solaris():
            return "Solaris"
        else:
            return "Unknown"

    def get_service_at(self, port, protocol):
        for service in self.services:
            if service.port == port and service.protocol == protocol:
                return service
        return None

    def resume_from_file(self, file_path):
        file = open(file_path, "r")
        raw = file.read()
        ctx = None

        for raw_line in raw.split("\n"):
            line = raw_line.strip()
            parts = line.split(" ")

            if line.startswith("#") or line == "":
                continue
            elif line.startswith("BEGIN"):
                ctx = line.split(" ")[1]
            else:
                if ctx == "META":
                    continue
                elif ctx == "SERVICES":
                    port = int(parts[0])
                    protocol = parts[1]
                    service_name = parts[2]
                    service_version = " ".join(parts[3:])
                    service = Service(self.target, port, protocol, service_name, service_version)
                    super().debug(f"* Recovered service {port}/{protocol} - {service_name} | {service_version}")
                    self.services.append(service)
                elif ctx == "OS":
                    key = parts[0]
                    value = " ".join(parts[1:])
                    if key == "ttl":
                        self.ttl = int(value)
                else:
                    super().error(f"* Failed parsing session file. Unknown context {ctx}")
                    return False
        return True

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
                service = Service(self.target, port, protocol, "unknown", "unknown")
                self.services.append(service)
                super().debug(f"* Found open port {port} ({protocol})")
            elif "You requested a scan type which requires root privileges" in line:
                super().error("* You need to run this script as root.")
                return False
            elif "open" in line and ("/tcp" in line or "/udp" in line):
                raw_port = line.split()[0]
                port = int(raw_port.split("/")[0])
                protocol = raw_port.split("/")[1]
                service_name = line.split()[2]
                service = self.get_service_at(port, protocol)
                service.name = service_name
                super().debug(f"* Discovered service running on {port} ({protocol})")
            elif "ttl" in line:
                raw_ttl = line.split()[5]
                self.ttl = int(raw_ttl)
        return True

    def search_exploits_for(self, service):
        id = service.get_info()
        cmd = ["searchsploit", "-w", "-t", "-j", "--disable-colour", "-t", id]
        out = subprocess.check_output(cmd, shell=False, stderr=subprocess.STDOUT, universal_newlines=True)
        result = json.loads(out)
        raw_exploits = result["RESULTS_EXPLOIT"]

        if len(raw_exploits) == 0:
            super().info(f"* No exploit found for {id}")
        else:
            super().ok(f"* Found exploits for {service}")

        index = 0
        for raw_exploit in raw_exploits:
            index += 1
            title = raw_exploit["Title"]
            url = raw_exploit["URL"]
            exploit = {"title": title, "url": url}
            self.exploits.append(exploit)
            print(f"         {Fore.YELLOW}#{str(index)} {Fore.LIGHTRED_EX}{title}")
            print(f"              {url}")

    def search_exploits(self):
        for service in self.services:
            if service.has_info():
                self.search_exploits_for(service)
            else:
                super().warn(f"* Skipping {service} because it has not enough information")

    def __str__(self) -> str:
        return "Scanner"
