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

        # Parse type
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

        # Parse on success
        if "on_success" in raw_action:
            self.on_success = raw_action['on_success']
        else:
            self.on_success = "success"

        # Parse reason
        if "reason" in raw_action:
            self.reason = raw_action['reason']
        else:
            self.reason = "failed"

    def _parse_rules(self):
        self.rules = []
        if not "rules" in self.raw_action:
            return

        for raw_rule in self.raw_action['rules']:
            self.rules.append(ActionRule(raw_rule))


def parse_actions(raw_actions):
    actions = []
    for raw_action in raw_actions:
        actions.append(Action(raw_action))
    return actions
