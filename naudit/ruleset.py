from service import Service
from match_utils import is_match_str

class Rule:
    def __init__(self, raw_rule):
        self.raw_rule = raw_rule

    def match(self, service: Service):
        if "port" in self.raw_rule and service.port != self.raw_rule['port']:
            return False

        if "service" in self.raw_rule:
            match_str = self.raw_rule['service']
            if not is_match_str(service.name, match_str):
                return False

        if "version" in self.raw_rule:
            match_str = self.raw_rule['version']
            if not is_match_str(service.version, match_str):
                return False

        return True


class RuleSet:
    def __init__(self, raw_rules = []):
        self.rules = []
        for raw_rule in raw_rules:
            rule = Rule(raw_rule)
            self.rules.append(rule)

    def match(self, service: Service):
        for rule in self.rules:
            if rule.match(service):
                return True
        return False


