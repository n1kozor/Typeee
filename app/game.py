import random
import base64

class Game:
    fruits = [
        "apple", "banana", "cherry", "grape", "lemon", "melon", "orange", "peach", "pear",
        "apricot", "avocado", "blackberry", "blueberry", "boysenberry", "cantaloupe", "coconut",
        "cranberry", "currant", "date", "dragonfruit", "elderberry", "fig", "gooseberry",
        "grapefruit", "guava", "honeydew", "kiwi", "kumquat", "lime", "lychee", "mango",
        "mulberry", "nectarine", "papaya", "passionfruit", "persimmon", "pineapple", "plum",
        "pomegranate", "quince", "raspberry", "starfruit", "strawberry", "tangerine", "watermelon"
    ]

    @staticmethod
    def shuffle_keyboard():
        letters = 'abcdefghijklmnopqrstuvwxyz'
        shuffled = ''.join(random.sample(letters, len(letters)))
        key_map = {letters[i]: shuffled[i] for i in range(len(letters))}
        return key_map

    @staticmethod
    def encode_key_map(key_map):
        key_map_str = ''.join(f'{k}:{v},' for k, v in key_map.items()).rstrip(',')
        return base64.b64encode(key_map_str.encode()).decode()

    @staticmethod
    def decode_key_map(encoded_key_map):
        decoded_str = base64.b64decode(encoded_key_map.encode()).decode()
        return {item.split(':')[0]: item.split(':')[1] for item in decoded_str.split(',')}

    @staticmethod
    def get_random_fruit():
        return random.choice(Game.fruits)
