from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import numpy as np
import requests
from collections import Counter
import os
import zlib
import struct

app = Flask(__name__)
CORS(app)

def base64_to_passcodes(base64_string):
    return np.frombuffer(base64.b64decode(base64_string), dtype=np.uint32)

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

class FormatDecodeException(Exception):
    pass

class OmegaFormatDecoder:
    def decode(self, encoded):
        encoded = encoded.strip()

        deflated = base64.b64decode(encoded)
        if deflated is None:
            raise FormatDecodeException("could not decode base64")

        try:
            raw = zlib.decompress(deflated, -zlib.MAX_WBITS)
        except zlib.error as e:
            raise FormatDecodeException(f"could not inflate compressed data: {e}")

        main_and_extra_count, raw = self.unpack('B', raw)
        side_count, raw = self.unpack('B', raw)

        deck_list = {
            "main": [],
            "extra": [],
            "side": []
        }

        for _ in range(main_and_extra_count):
            code, raw = self.unpack_code(raw)
            if len(deck_list["main"]) < 40:
                deck_list["main"].append(code)
            else:
                deck_list["extra"].append(code)

        for _ in range(side_count):
            code, raw = self.unpack_code(raw)
            deck_list["side"].append(code)

        return deck_list

    def unpack_code(self, data):
        return self.unpack('I', data)

    def unpack(self, format, data):
        size = struct.calcsize(format)
        unpacked = struct.unpack(format, data[:size])
        if not unpacked:
            raise FormatDecodeException("unexpected end of input")

        return unpacked[0], data[size:]

def fetch_card_name(card_id):
    url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?id={card_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "data" in data and len(data["data"]) > 0:
            return data["data"][0]["name"]
    return None

def fetch_names_for_ids(deck):
    card_names_dict = {}
    for category, ids_array in deck.items():
        names = [fetch_card_name(card_id) for card_id in ids_array]
        card_names_dict[category] = Counter(names)
    return card_names_dict

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    url_string = data.get('url')
    if not url_string:
        return jsonify({"error": "URL is required"}), 400

    try:
        if url_string.startswith("ydke://"):
            card_ids = parse_url(url_string)
            card_names = fetch_names_for_ids({
                "main": card_ids.main,
                "extra": card_ids.extra,
                "side": card_ids.side
            })
        elif any(c.isalpha() for c in url_string) and "+" in url_string:
            decoder = OmegaFormatDecoder()
            deck_list = decoder.decode(url_string)
            card_names = fetch_names_for_ids(deck_list)
        else:
            return jsonify({"error": "Invalid format"}), 400
        
        result = {}
        for category, names_counter in card_names.items():
            result[category] = {name: count for name, count in names_counter.items()}
        
        return jsonify(result)
    except FormatDecodeException as e:
        return jsonify({"error": f"Decoding error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 5000)))
