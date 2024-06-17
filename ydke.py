import base64
import re
import numpy as np

def base64_to_passcodes(base64_string):
    return np.frombuffer(base64.b64decode(base64_string), dtype=np.uint32)

def passcodes_to_base64(passcodes):
    return base64.b64encode(passcodes.tobytes()).decode('utf-8')

class TypedDeck:
    def __init__(self, main, extra, side):
        self.main = main
        self.extra = extra
        self.side = side

def parse_url(ydke_url):
    if not ydke_url.startswith("ydke://"):
        raise ValueError("Unrecognized URL protocol")

    components = ydke_url[len("ydke://"):].split("!")
    if len(components) < 3:
        raise ValueError("Missing ydke URL component")

    return TypedDeck(
        main=base64_to_passcodes(components[0]),
        extra=base64_to_passcodes(components[1]),
        side=base64_to_passcodes(components[2])
    )

def to_url(deck):
    return "ydke://" + \
        passcodes_to_base64(deck.main) + "!" + \
        passcodes_to_base64(deck.extra) + "!" + \
        passcodes_to_base64(deck.side) + "!"

def extract_urls(from_string):
    ydke_reg = re.compile(r'ydke://[A-Za-z0-9+/=]?![A-Za-z0-9+/=]?![A-Za-z0-9+/=]*?!')
    return ydke_reg.findall(from_string)
