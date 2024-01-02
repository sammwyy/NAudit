import json
import os

from actionset import ActionSet
from ruleset import RuleSet

class Payload:
    def __init__(self, file_path):
        self.file_path = file_path
        self.name = os.path.basename(file_path).replace(".json", "")
        self._parse()

    def _parse(self):
        file = open(self.file_path, "r")
        raw = file.read()
        self.data = json.loads(raw)
        self.actionset = ActionSet(self.name, self.data['actions'])
        self.ruleset = RuleSet(self.data['rules'])

    def match(self, service):
        return self.ruleset.match(service)

    def run(self):
        self.actionset.exec()

    def __str__(self):
        return self.name
