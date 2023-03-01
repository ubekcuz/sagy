# made by V¡ktor
# 2023-02-25
# thanks for using box.py <3

import os
from datetime import datetime
from random import choice
from string import (
    ascii_letters,
    digits
)

from pytz import timezone


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def tzFilter(hour=23, *, gmt=None):
    # Examples:
    # >>> tzFilter(hour=18)
    # -300
    #
    # >>> tzFilter(gmt=5)
    # -300
    zones = ('Etc/GMT' + (f'+{i}' if i > 0 else str(i)) for i in range(-12, 12))
    for _ in (['Etc/GMT' + (f'+{gmt}' if gmt > 0 else str(gmt))] if isinstance(gmt, int) else zones):
        zone = datetime.now(timezone(_))
        if not gmt and int(zone.strftime('%H')) != hour:
            continue
        return int(zone.strftime('%Z').replace('GMT', '00')) * 60


def randomCode(length=15, chars=None):
    # Example:
    # >>> randomCode(length = 8, chars = "aeiou12345")
    # '552ei4o4'
    return "".join(choice(
        list(chars) if chars else list(ascii_letters + digits + "!@#$%&")
    ) for _ in range(length))
