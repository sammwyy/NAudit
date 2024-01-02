from colorama import Fore
import enum
import subprocess
import threading

from match_utils import is_match_str
from loggable import Loggable

class ActionType(enum.Enum):
    SHELL = 1
    BREAK = 2

def get_action_type(action):
    fixed = action.lower()
    if fixed == "shell":
        return ActionType.SHELL
    elif fixed == "break":
        return ActionType.BREAK
    else:
        raise Exception("Unknown action type: " + action)

class ActionRule:
    def __init__(self, raw_rule):
        self.raw_rule = raw_rule
        self.prev_stdout = None
        self._parse()

    def _parse(self):
        if "prev_stdout" in self.raw_rule:
            self.prev_stdout = self.raw_rule['prev_stdout']

class Action:
    def __init__(self, raw_action):
        self.raw_action = raw_action
        self._parse()
        self._parse_rules()

    def _parse(self):
        raw_action = self.raw_action
        self.type = get_action_type(raw_action['type'])

        # Parse argument
        if "args" in raw_action:
            self.arg = raw_action['args']
        else:
            self.arg = None

        # Parse rule miss
        if "on_rules_miss" in raw_action:
            self.rule_miss = Action(raw_action['on_rules_miss'])
        else:
            self.rule_miss = None

    def _parse_rules(self):
        self.rules = []
        if not "rules" in self.raw_action:
            return

        for raw_rule in self.raw_action['rules']:
            self.rules.append(ActionRule(raw_rule))


class ActionSet(Loggable):
    def __init__(self, payload_name, actions = []):
        self.payload_name = payload_name
        self.actions = []
        for action in actions:
            self.actions.append(Action(action))

    def exec(self):
        prev_stdout = None
        failed = False
        stage = 0

        for action in self.actions:
            stage += 1

            # Check is must be executed
            for rule in action.rules:
                if rule.prev_stdout != None and not is_match_str(prev_stdout, rule.prev_stdout):
                    failed = True

            # Check is failed
            if failed:
                if action.rule_miss != None:
                    super().error(f"Stage {stage} failed.")
                    action = action.rule_miss
                else:
                    super().error(f"Stage {stage} failed, skipping.")
                    continue

            # Run action
            if action.type == ActionType.SHELL:
                cmd = action.arg
                prev_stdout = subprocess.check_output(cmd, shell = True, encoding = "utf-8")
                if not failed:
                    super().ok(f"Stage {stage} success.")
            elif action.type == ActionType.BREAK:
                if failed:
                    super().error(f"Payload failed, breaking.")
                return


    def async_exec(self):
        self.thread = threading.Thread(target=self.exec)
        self.thread.start()

    def __str__(self) -> str:
        return "Payload"
