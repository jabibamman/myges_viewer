import json
import os
from utils import logger_utils as log
from utils.config_utils import username
from utils.json_utils import load_json

def get_marks_json(year,semester):
    filename = f"data/{username}/marks/marks_{year}_semester_{semester}.json"
    if os.path.exists(filename):
        data = load_json(filename)
        return data, 200
    else:
        return {"error": "File does not exist"}, 404

def write_to_json(final_dict, filename, directory="out", ):
    log.get_logger().info(f"Writing data to {filename}")
    if not os.path.exists(f"data/{username}/{directory}"):
        os.makedirs(f"data/{username}/{directory}")

    with open(f"data/{username}/{directory}/{filename}", "w", encoding='utf-8') as f:
        json.dump(final_dict, f, indent=4)