#!/usr/bin/env python3

import requests
import time

from style import draw_data, print_data
from colors import terminal_colors
from asus import Asus, SessionExpiredException

# drawn | print | graph
style = "drawn"

asus = Asus()

while True:
    # Caches the config and sign in details under the hood
    if not asus.configured:
        asus.configure()

    time.sleep(1)
    try:
        data = asus.get_cpu_memory()
    except requests.exceptions.Timeout:
        if style == "drawn":
            print(terminal_colors.fg.red + "!" + terminal_colors.reset, end="")
        elif style == "print":
            print("Timeout..")
        continue
    except requests.exceptions.ConnectionError:
        if style == "drawn":
            print(terminal_colors.fg.red + "!" + terminal_colors.reset, end="")
        elif style == "print":
            print("Connection error..")
        continue
    except SessionExpiredException:
        print("Login token expired, you need to sign in again")
        asus.login()
        continue

    if style == "drawn":
        draw_data(data)
    elif style == "print":
        print_data(data)
    elif style == "graph":
        exit(1)
        
