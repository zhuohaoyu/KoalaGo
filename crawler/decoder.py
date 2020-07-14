import json

with open("./data_norm/8097.json", "r") as f:
    s = f.read()
    text = json.loads(s)
    print(text)