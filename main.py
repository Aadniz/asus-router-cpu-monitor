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


# From Asus's source code:
# var pt = "";
# var percentage = total_diff = usage_diff = 0;
# var length = Object.keys(cpu_info_new).length;
# for(i=0;i<length;i++){
#   pt = "";
#   total_diff = (cpu_info_old[i].total == 0)? 0 : (cpu_info_new["cpu"+i].total - cpu_info_old[i].total);
#   usage_diff = (cpu_info_old[i].usage == 0)? 0 : (cpu_info_new["cpu"+i].usage - cpu_info_old[i].usage);
#   percentage = (total_diff == 0) ? 0 : parseInt(100*usage_diff/total_diff);
#   $("#cpu"+i+"_bar").css("width", percentage +"%");
#   $("#cpu"+i+"_quantification").html(percentage +"%");
#   cpu_usage_array[i].push(100 - percentage);
#   cpu_usage_array[i].splice(0,1);
#   for(j=0;j<array_size;j++){
#     pt += j*6 +","+ cpu_usage_array[i][j] + " ";
#   }
#   document.getElementById('cpu'+i+'_graph').setAttribute('points', pt);
#   cpu_info_old[i].total = cpu_info_new["cpu"+i].total;
#   cpu_info_old[i].usage = cpu_info_new["cpu"+i].usage;
# }

cpu_info_old = []

while True:
    r = requests.get(f"http://{host}/cpu_ram_status.asp?_={int(time.time() * 1000)}", proxies=proxies, cookies=cookies, headers=headers)
    content = extract_jsons(r.text)
    

    percentage = total_diff = usage_diff = 0
    length = len(content["cpuInfo"].keys())
    for i in range(length):
        # Esnure cpu_info_old is set
        if i >= len(cpu_info_old):
            cpu_info_old.append({
                "total": 0,
                "usage": 0
            })
        pt = ""
        total_diff = 0 if cpu_info_old[i]["total"] == 0 else int(content["cpuInfo"][f"cpu{i}"]["total"]) - int(cpu_info_old[i]["total"])
        usage_diff = 0 if cpu_info_old[i]["usage"] == 0 else int(content["cpuInfo"][f"cpu{i}"]["usage"]) - int(cpu_info_old[i]["usage"])
        percentage = '{0:.2f}'.format(0 if total_diff == 0.00 else float(100*usage_diff/total_diff));
        cpu_info_old[i]["total"] = int(content["cpuInfo"][f"cpu{i}"]["total"])
        cpu_info_old[i]["usage"] = int(content["cpuInfo"][f"cpu{i}"]["usage"])
        print(f"cpu{i}: {percentage}%", end=" ")
    
    
    percentage = '{0:.2f}'.format(float(content['memInfo']['used']) / float(content['memInfo']['total']) * 100)
    print(f"mem: {percentage}%")
    time.sleep(1)
