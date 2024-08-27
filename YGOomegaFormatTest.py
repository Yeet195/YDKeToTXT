import base64
import zlib
import struct
import requests
from collections import Counter

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

        # Unpacking counts for main/extra and side decks
        main_and_extra_count, raw = self.unpack('B', raw)
        side_count, raw = self.unpack('B', raw)

        deck_list = {
            "main": [],
            "extra": [],
            "side": []
        }

        # Decode main and extra decks
        for _ in range(main_and_extra_count):
            code, raw = self.unpack_code(raw)
            if len(deck_list["main"]) < 40:  # Assuming main deck is always up to 40 cards first
                deck_list["main"].append(code)
            else:
                deck_list["extra"].append(code)

        # Decode side deck
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

def fetch_names_for_ids(deck_list):
    card_names_dict = {}
    for category in ["main", "extra", "side"]:
        names = [fetch_card_name(card_id) for card_id in deck_list[category]]
        card_names_dict[category] = Counter(names)
    return card_names_dict

def main():
    encoded_string = input("Enter the encoded string: ").strip()
    
    decoder = OmegaFormatDecoder()
    
    try:
        deck_list = decoder.decode(encoded_string)
        card_names = fetch_names_for_ids(deck_list)
        
        result = {}
        for category, names_counter in card_names.items():
            result[category] = {name: count for name, count in names_counter.items()}
        
        for category, cards in result.items():
            print()
            for name, count in cards.items():
                print(f"{count}x {name}")
    
    except FormatDecodeException as e:
        print(f"Error decoding: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
