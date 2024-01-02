from enum import Enum

class MatchMode (Enum):
    EXACT = 1
    STARTS_WITH = 2
    ENDS_WITH = 3
    CONTAINS = 4

def get_match_mode(str):
    starts_with = str.startswith("*")
    ends_with = str.endswith("*")

    if starts_with and ends_with:
        return MatchMode.CONTAINS
    elif starts_with:
        return MatchMode.ENDS_WITH
    elif ends_with:
        return MatchMode.STARTS_WITH
    else:
        return MatchMode.EXACT

def is_match_str(string, match_str):
    match_mode = get_match_mode(match_str)
    fixed = match_str.replace("*", "")

    if match_mode == MatchMode.EXACT:
        return string == fixed
    elif match_mode == MatchMode.STARTS_WITH:
        return string.startswith(fixed)
    elif match_mode == MatchMode.ENDS_WITH:
        return string.endswith(fixed)
    elif match_mode == MatchMode.CONTAINS:
        return fixed in string
