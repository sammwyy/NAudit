import click
import file_utils
import sys
from loggable import Loggable
from payload import Payload
from scanner import Scanner

class NAudit(Loggable):
    def __init__(self):
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

    def run(self, opts):
        target = opts.get("target")

        super().info(f"Performing network audit on {target}")
        scanner = Scanner(target)

        super().info("Performing port scan.")
        if not scanner.scan_ports():
            sys.exit(1)

        super().info("Performing service scan.")
        services = scanner.scan_services()
        if services is None:
            sys.exit(1)

        if len(services) == 0:
            super().warn("No services found, exiting.")
            sys.exit(0)

        super().info("Performing payload execution.")
        executions = 0
        for service in services:
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
    naudit = NAudit()
    opts = {"target": target}
    naudit.run(opts)

if __name__ == "__main__":
    main()
