import requests
import os
import numpy as np
from collections import Counter
from tqdm import tqdm
from ydke import parse_url

url = input("Enter YDKe link:\n")
os.system('cls' if os.name == 'nt' else 'clear')

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
        names = [fetch_card_name(card_id) for card_id in tqdm(ids_array, desc=f"Fetching and constructiong {category} deck")]
        card_names_dict[category] = Counter(names)
    return card_names_dict

# Given list of IDs
card_ids = parse_url(url)

# Fetch names for the IDs
card_names = fetch_names_for_ids(card_ids)

# Display the results
for category, names_counter in card_names.items():
    for name, count in names_counter.items():
        print(f"{count}x {name}")

input("Enter to exit")
