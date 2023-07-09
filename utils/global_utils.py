import json
import os

from bs4 import BeautifulSoup

from utils import logger_utils as log


def write_to_console(final_dict):
    """
    TODO: Pas encore bien implémentée
    Affiche le planning dans la console
    :param final_dict:
    :return:
    """
    for key, value in final_dict.items():
        log.get_logger().info(key, ':', value)


def week_difference(date1, date2):
    """Calcule le nombre de semaines entre deux dates."""
    return int((date2 - date1).days / 7)


def compare_html(soup, filename):
    """
    Compare BeautifulSoup object with existing HTML file.
    Returns True if they are identical, False otherwise.
    """
    if not os.path.isfile(filename):
        return False

    with open(filename, 'r', encoding='utf-8') as file:
        existing_html = file.read()

    existing_soup = BeautifulSoup(existing_html, 'html.parser')
    return soup == existing_soup


def write_html(soup, filename):
    """
    Write BeautifulSoup object to an HTML file.
    """
    html = soup.prettify()

    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html)

def write_to_json(final_dict, filename):
    log.get_logger().info(f"Writing data to {filename}")
    with open(f"data/{filename}", 'w', encoding='utf-8') as f:
        json.dump(final_dict, f, indent=4)
