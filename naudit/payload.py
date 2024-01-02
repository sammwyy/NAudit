import json
import os
import subprocess
import threading

from action import ActionType, parse_actions
from loggable import Loggable
from match_utils import is_match_str
from ruleset import RuleSet

class Payload(Loggable):
    def __init__(self, file_path):
        self.file_path = file_path
        self.name = os.path.basename(file_path).replace(".json", "")
        self._parse()

    def _parse(self):
        file = open(self.file_path, "r")
        raw = file.read()
        payload_data = json.loads(raw)
        self.id = payload_data['id']
        self.actions = parse_actions(payload_data['actions'])
        self.ruleset = RuleSet(payload_data['rules'])

    def match(self, service):
        return self.ruleset.match(service)

    def run_action(self, action, service):
        if action.type == "shell":
            self.run_shell(action, service)
        elif action.type == "break":
            self.run_break(action, service)
        else:
            raise Exception("Unknown action type: " + action.type)

    def _internal_format(self, string, stdio, service):
        out = string.replace("$service", service.name)
        out = out.replace("$address", service.address)
        out = out.replace("$port", str(service.port))
        out = out.replace("$protocol", str(service.protocol))
        out = out.replace("$prev_stdout", stdio)
        return out

    def run(self, service):
        prev_stdout = ""
        failed = False
        stage = 0

        for action in self.actions:
            stage += 1

            # Check if must be executed
            for rule in action.rules:
                if rule.prev_stdout != None and not is_match_str(prev_stdout, rule.prev_stdout):
                    failed = True

            # Check if failed
            if failed:
                if action.rule_miss != None:
                    action = action.rule_miss
                else:
                    super().warn(f"Stage {str(stage)}: {action.reason}, skipping.")
                    continue

            # Execute action
            if action.type == ActionType.SHELL:
                cmd = self._internal_format(action.arg, prev_stdout, service)
                prev_stdout = subprocess.check_output(cmd, shell = True, encoding = "utf-8")
                msg = self._internal_format(action.on_success, prev_stdout, service)
                super().ok(f"Stage {str(stage)}: {msg}")
            elif action.type == ActionType.BREAK:
                msg = self._internal_format(action.reason, prev_stdout, service)
                if failed:
                    super().error(f"Stage {str(stage)}: {msg}")
                else:
                    super().warn(f"Stage {str(stage)}: {msg}")
                return

    def run_async(self):
        self.thread = threading.Thread(target=self.exec)
        self.thread.start()

    def __str__(self):
        return f"payload:{self.id}"
