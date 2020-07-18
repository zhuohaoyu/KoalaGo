import json

with open("../data/2333.json", "r") as f:
    s = f.read()
    text = json.loads(s)
    print(text)