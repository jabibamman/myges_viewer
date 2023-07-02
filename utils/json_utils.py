import json


def write_to_json(data, file_name):
    with open("data/"+file_name, "w") as f:
        json.dump(data, f, indent=4)