import json

from utils.logger_utils import get_logger


def read_config():
    try:
        with open('config.json') as f:
            config = json.load(f)
        return config['myges']['username'], config['myges']['password'], config['discord']['token'], \
            config['discord']['id']
    except FileNotFoundError:
        logger = get_logger()
        logger.error(f"Config file not found, please create a config.json file in the root directory")
        exit(1)


username, password, secret_discord, discord_channel = read_config()
