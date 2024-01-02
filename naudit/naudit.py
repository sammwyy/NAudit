import click
import file_utils
import os
import sys

from loggable import Loggable
from payload import Payload
from scanner import Scanner

class NAudit(Loggable):
    def __init__(self, opts):
        self.opts = opts
        self.target = opts.get("target")
        self.scanner = Scanner(self.target)
        self.payloads = []
        self._load_payload()

    def _load_payload(self):
        dir = file_utils.get_path("payloads")
        files = file_utils.walk_dir(dir, ".json")
        amount = 0

        for file in files:
            payload = Payload(file)
            self.payloads.append(payload)
            amount += 1
        super().info(f"Loaded {amount} payloads.")

    def attack_service(self, service):
        for payload in self.payloads:
            if payload.match(service):
                super().info(f"* Running payload {payload} for service {service}")
                payload.run()
                return True
        return False

    def recover(self, file):
        super().warn(f"Session was resumed and recovered services from previous scan.")
        super().warn("If you want to perform a new scan, delete the results_*.txt file or run the script with the --force flag.")

        if not self.scanner.resume_from_file(file):
            sys.exit(1)

        # OS scanner.
        os_name = self.scanner.get_os()
        super().info(f"Recognized OS: {os_name}")

    def scan(self, results_file_path):
        # Port scanner.
        super().info("Performing port scan.")
        if not self.scanner.scan_ports():
            sys.exit(1)

        # OS scanner.
        os_name = self.scanner.get_os()
        super().info(f"Recognized OS: {os_name}")

        # Save results to file.
        services = self.scanner.services
        results_file = open(results_file_path, "w")
        results_file.write(f"# NAudit results file\n")
        results_file.write(f"BEGIN META\ntimestamp {super()._get_full_timestamp()}\ntarget {self.target}\n\n")
        results_file.write("BEGIN SERVICES\n")
        for service in services:
            results_file.write(f"{service.port} {service.protocol} {service.name} {service.version}\n")
        results_file.write(f"\nBEGIN OS\nttl {self.scanner.ttl}\n")

    def run(self):
        super().info(f"Performing network audit on {self.target}")

        # Previous scan recovery.
        recover_file = file_utils.get_path(f"results_{self.target}.txt")
        must_recover = self.opts.get("force") is None and os.path.exists(recover_file)

        if must_recover:
            self.recover(recover_file)
        else:
            self.scan(recover_file)

        # Abort if no services were found.
        if len(self.scanner.services) == 0:
            super().warn("No services found, exiting.")
            sys.exit(0)

        # Exploit enumeration.
        super().info("Performing exploit enumeration.")
        self.scanner.search_exploits()

        # Exploit execution.
        super().info("Performing payload execution.")
        executions = 0
        for service in self.scanner.services:
            if self.attack_service(service):
                executions += 1

        if executions == 0:
            super().warn("No payloads executed, exiting.")
            sys.exit(0)

    def __str__(self) -> str:
        return "NAudit"

@click.command()
@click.argument("target")
def main(target):
    banner = """
    ,--.  ,--.  ,---.             ,--.,--.  ,--.
    |  ,'.|  | /  O  \ ,--.,--. ,-|  |`--',-'  '-.
    |  |' '  ||  .-.  ||  ||  |' .-. |,--.'-.  .-'
    |  | `   ||  | |  |'  ''  '\ `-' ||  |  |  |
    `--'  `--'`--' `--' `----'  `---' `--'  `--'
           Created by Sammwy | version 0.1
"""

    print(banner)
    opts = {"target": target}
    naudit = NAudit(opts)
    naudit.run()

if __name__ == "__main__":
    main()
