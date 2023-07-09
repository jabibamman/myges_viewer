import json


def write_to_json(data, file_name):
    with open("data/" + file_name, "w") as f:
        json.dump(data, f, indent=4)


def read_json(file):
    with open("data/" + file, "r") as f:
        return json.load(f)


def read_json_as_lists(file):
    with open("data/" + file, "r") as f:
        data = json.load(f)
    return list(data.keys()), list(data.values())


def load_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data