#!/usr/bin/env python3

# Minimal request needed to get relevant output:
# curl -x socks5h://127.0.0.1:2522 \
#    -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0' \
#    -H 'Cookie: asus_token=IXD8CQWnJrLLp7opz3KxotDze6LQkTB' \
#    'http://192.168.1.1/cpu_ram_status.asp?_=1775146845520'

import requests
import re
import json
import time

VALID_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"
VALID_ASUS_TOKEN = "ctKWXmJW9inW5bP9dQQqB6a9VPp9Hq0"


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


#proxy = input("Plz enter socks proxy floof: ")
proxy = "127.0.0.1:2522"
#host = input("Plz enter host floof: ")
host = "192.168.1.1"

proxies = {
    "http": f"socks5h://{proxy}",
    "https": f"socks5h://{proxy}"
}
headers = {
    "User-Agent": VALID_USER_AGENT
}
cookies = {
    "asus_token": VALID_ASUS_TOKEN
}


while True:
    r = requests.get(f"http://{host}/cpu_ram_status.asp?_={int(time.time() * 1000)}", proxies=proxies, cookies=cookies, headers=headers)
    content = extract_jsons(r.text)
    
    cpus = list(content["cpuInfo"].keys())
    for cpu in cpus:
        percentage = '{0:.2f}'.format(float(content["cpuInfo"][cpu]["usage"]) / float(content["cpuInfo"][cpu]["total"]) * 100)
        print(f"{cpu}: {percentage}%", end=" ")
    percentage = '{0:.2f}'.format(float(content['memInfo']['used']) / float(content['memInfo']['total']) * 100)
    print(f"mem: {percentage}%")
    time.sleep(1)
