import re

def parse_query(query):
    pattern = r"""
    SELECT\s+(?P<indicator>\w+)\s+
    FROM\s+(?P<asset>\w+)\s+
    WHERE\s+CHANGE=(?P<change>-?\d+\.?\d*)\s+
    SIM=(?P<sim>\d+)
    """

    match = re.search(pattern, query, re.VERBOSE | re.IGNORECASE)

    if not match:
        raise ValueError("Invalid query format")

    return {
        "indicator": match.group("indicator").upper(),
        "change": float(match.group("change")),
        "asset": match.group("asset").upper(),
        "sim": int(match.group("sim"))
    }

#print(parse_query("SELECT SMA20 FROM NQ WHERE CHANGE=20 SIM=100"))