from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import numpy as np
import requests
from collections import Counter
import os

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
    for category, ids_array in [("main", deck.main), ("extra", deck.extra), ("side", deck.side)]:
        names = [fetch_card_name(card_id) for card_id in ids_array]
        card_names_dict[category] = Counter(names)
    return card_names_dict

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    ydke_url = data.get('url')
    if not ydke_url:
        return jsonify({"error": "URL is required"}), 400

    try:
        card_ids = parse_url(ydke_url)
        card_names = fetch_names_for_ids(card_ids)
        
        result = {}
        for category, names_counter in card_names.items():
            result[category] = {name: count for name, count in names_counter.items()}
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 5000)))
