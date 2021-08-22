import json

import algo


def process(file):
    try:
        data = json.load(file)
        return algo.generate_header(data)
    except:
        print("went wrong")
        return []
