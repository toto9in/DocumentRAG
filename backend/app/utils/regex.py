import re

def extract_value(s):
    match = re.search(r'R\$ [\dX\.]*,[\dX]{2}', s)
    if match:
        return match.group(0)
    else:
        return None
