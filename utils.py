#!/usr/bin/env python3

import json
import re

def extract_variable_backwards(content: str) -> str|None:
    content = content.lstrip()
    if content[0] != "=":
        return None
    capture = re.search(r'=(?:\s+|)(\S+)', content)
    if capture:
        return (capture.group(1))[::-1]
    return None


def extract_jsons(content) -> dict:
    data: dict = {}
    start_pos: int | None = None
    pos: int = 0
    depth: int = 0
    # Skip forward until it finds a starting curly bracket "{"
    for ch in content:
        if ch == "{":
            if depth == 0:
                start_pos = pos
            depth += 1
        elif ch == "}":
            if depth == 1 and start_pos is not None:
                # Here we are done capturing the entire JSON
                json_content_str = content[start_pos:pos + 1]
                try:
                    json_content = json.loads(json_content_str)
                    variable = extract_variable_backwards(content[start_pos-len(content)-1::-1])
                    if variable is None:
                        if "unnamed" not in data:
                            data["unnamed"] = []
                        data["unnamed"].append(json_content)
                    data[variable] = json_content
                except ValueError as e:
                    pass
                start_pos = None
            depth = max(depth - 1, 0)
        pos += 1
    return data
