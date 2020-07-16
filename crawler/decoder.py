import json

with open("../data/1526.json", "r") as f:
    s = f.read()
    text = json.loads(s)
    print(text)