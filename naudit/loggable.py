from colorama import Fore
import time

def right_pad(string, width):
    return " " + string + " " * (width - 1 - len(string))

class Loggable():
    def __init__(self):
        pass

    def _get_timestamp(self):
        return time.strftime("%H:%M:%S", time.localtime())

    def _print(self, message):
        time = self._get_timestamp()
        id = right_pad(str(self), 10)
        print(f"{Fore.LIGHTBLACK_EX}{time} {Fore.LIGHTMAGENTA_EX}[{id}] {message}")

    def info(self, message):
        self._print(f"{Fore.LIGHTCYAN_EX}INFO  {Fore.CYAN}{message}")

    def ok(self, message):
        self._print(f"{Fore.GREEN} OK   {Fore.LIGHTGREEN_EX}{message}")

    def warn(self, message):
        self._print(f"{Fore.YELLOW}WARN  {message}")

    def error(self, message):
        self._print(f"{Fore.LIGHTRED_EX}CRIT  {Fore.RED}{message}")

    def debug(self, message):
        self._print(f"{Fore.LIGHTBLACK_EX}DEBUG {Fore.WHITE}{message}")

