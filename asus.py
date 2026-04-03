#!/usr/bin/env python3

import os
import requests
import time
import base64
from getpass import getpass

from utils import extract_jsons


VALID_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"


class SessionExpiredException(Exception):
    pass


class Asus:
    host: str | None = "192.168.1.1:80"
    proxy: str | None = None
    configured: bool = False
    __asus_token: str | None = None
    __cached_asus_token_path: str = os.path.dirname(os.path.realpath(__file__)) + "/.cached_token"

    __cpu_info_old = []

    def __init__(self):
        self.__load_cached_token()

    def configure(self):
        proxy = input("Enter socks proxy (default: None): ")
        if proxy != "":
            self.proxy = proxy
        host = input("Enter host (default: 192.168.1.1:80): ")
        if host != "":
            self.host = host
        self.configured = True
    
    def login(self):
        username = input("Enter username: ")
        password = getpass()
        headers = {
            'User-Agent': VALID_USER_AGENT,
            'Referer': f"http://{self.host}/Main_Login.asp"
        }
        payload = {
            'login_authorization': base64.b64encode((f"{username}:{password}").encode())
        }
        r = requests.post(f"http://{self.host}/login.cgi", headers=headers, data=payload, timeout=5)
        asus_token = r.cookies.get("asus_token")

        if not asus_token:
            return False

        self.__asus_token = asus_token
        self.__cache_token()
        return True

    def __cache_token(self):
        if not self.__asus_token:
            return

        with open(self.__cached_asus_token_path, "w") as f:
            f.write(self.__asus_token)

    def __load_cached_token(self):
        if os.path.isfile(self.__cached_asus_token_path):
            file = open(self.__cached_asus_token_path, "r")
            self.__asus_token = file.read()
    
    def __get_socks_proxies(self):
        if not self.proxy:
            return None
        return {
            "http": f"socks5h://{self.proxy}",
            "https": f"socks5h://{self.proxy}"
        }
        
    def get_cpu_memory(self):
        #From Asus's source code:
        #var pt = "";
        #var percentage = total_diff = usage_diff = 0;
        #var length = Object.keys(cpu_info_new).length;
        #for(i=0;i<length;i++){
        #  pt = "";
        #  total_diff = (cpu_info_old[i].total == 0)? 0 : (cpu_info_new["cpu"+i].total - cpu_info_old[i].total);
        #  usage_diff = (cpu_info_old[i].usage == 0)? 0 : (cpu_info_new["cpu"+i].usage - cpu_info_old[i].usage);
        #  percentage = (total_diff == 0) ? 0 : parseInt(100*usage_diff/total_diff);
        #  $("#cpu"+i+"_bar").css("width", percentage +"%");
        #  $("#cpu"+i+"_quantification").html(percentage +"%");
        #  cpu_usage_array[i].push(100 - percentage);
        #  cpu_usage_array[i].splice(0,1);
        #  for(j=0;j<array_size;j++){
        #    pt += j*6 +","+ cpu_usage_array[i][j] + " ";
        #  }
        #  document.getElementById('cpu'+i+'_graph').setAttribute('points', pt);
        #  cpu_info_old[i].total = cpu_info_new["cpu"+i].total;
        #  cpu_info_old[i].usage = cpu_info_new["cpu"+i].usage;
        #}
        if not self.__asus_token:
            raise SessionExpiredException("Asus token not set")

        proxies = self.__get_socks_proxies()
        headers = {
            "User-Agent": VALID_USER_AGENT
        }
        cookies = {
            "asus_token": self.__asus_token
        }
        r = requests.get(f"http://{self.host}/cpu_ram_status.asp?_={int(time.time() * 1000)}", proxies=proxies, cookies=cookies, headers=headers, timeout=1)
        text = r.text
        content = extract_jsons(text)

        if not content:
            raise SessionExpiredException(f"Was unable to get appropriate content: {text}")
        
        data = {}
    
        percentage = total_diff = usage_diff = 0
        length = len(content["cpuInfo"].keys())
        for i in range(length):
            # Esnure cpu_info_old is set
            if i >= len(self.__cpu_info_old):
                self.__cpu_info_old.append({
                    "total": 0,
                    "usage": 0
                })
            total_diff = 0 if self.__cpu_info_old[i]["total"] == 0 else int(content["cpuInfo"][f"cpu{i}"]["total"]) - int(self.__cpu_info_old[i]["total"])
            usage_diff = 0 if self.__cpu_info_old[i]["usage"] == 0 else int(content["cpuInfo"][f"cpu{i}"]["usage"]) - int(self.__cpu_info_old[i]["usage"])
            percentage = 0 if total_diff == 0.00 else float(100*usage_diff/total_diff)
            self.__cpu_info_old[i]["total"] = int(content["cpuInfo"][f"cpu{i}"]["total"])
            self.__cpu_info_old[i]["usage"] = int(content["cpuInfo"][f"cpu{i}"]["usage"])
            data[f"cpu{i}"] = percentage
    
        percentage = float(content['memInfo']['used']) / float(content['memInfo']['total']) * 100
        data["mem"] = percentage
        return data

    def __token_expired(self):
        pass
