from datetime import datetime
import os

from bs4 import BeautifulSoup
from utils import logger_utils as log
from utils.config_utils import username


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


def week_to_date_string(year, week_number):
    date = datetime.strptime(f'{year} {week_number} 1', "%Y %W %w")
    date_string = date.strftime("%d_%m_%y")
    date_string = date_string.lstrip("0")
    return date_string


def date_string_to_week_number(year, date_string):
    date = datetime.strptime(f'{year}_{date_string}', "%Y_%d_%m_%y")
    week_number = int(date.strftime("%W"))
    return week_number


def check_existing_json_files_for_week_range(year, start_week, end_date_string):
    end_week = date_string_to_week_number(year,
                                          end_date_string) - 1  # -1 because we don't want to check the current week
    print("end_week:", end_week, ",start_week:", start_week, ",end_date_string:", end_date_string)


    for week in range(start_week, end_week):
        date_string = week_to_date_string(year, week)
        print("test:", date_string)
        filename = f"data/{username}/schedule/semaine_du_{date_string}.json"

        if not os.path.exists(filename):
            return False

    return True
