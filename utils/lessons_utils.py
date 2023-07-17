import json
import os
import time
from datetime import datetime
import re

from selenium.common.exceptions import ElementClickInterceptedException

from scraper.selenium_utils import get_element_text, click_element
from utils import json_utils
from selenium.webdriver.common.by import By
from utils import logger_utils as log
from utils.config_utils import username
from utils.json_utils import load_json

def get_lessons_json(year,semester):
    filename = f"data/{username}/lessons/lessons_{year}_semester_{semester}.json"
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