import json
import locale
from datetime import datetime
import re
import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from scraper.selenium_utils import wait_for_element

from utils import schedule_utils as su
from utils import logger_utils as log
from utils import global_utils as util


class MyGesScraper:
    logger = log.get_logger()

    def __init__(self, driver, username, password):
        self.driver = driver
        self.username = username
        self.password = password

    def login(self):
        self.driver.get('https://www.myges.fr/login')

        username_input = wait_for_element(self.driver, By.ID, 'username', 0)
        password_input = wait_for_element(self.driver, By.ID, 'password', 0)

        username_input.send_keys(self.username)
        password_input.send_keys(self.password)

        login_button = wait_for_element(self.driver, By.NAME, 'submit', 0)
        login_button.click()

        if 'j_spring_cas_security_check' in self.driver.current_url:
            self.logger.error('Login failed')
            return False
        else:
            self.logger.info('Login successful, current url is: ' + self.driver.current_url)
            return True

    def get_schedule(self, to_json=True, to_mongo=False, to_Console=False, startOfTheYear=True):
        """
        Récupère le planning de l'utilisateur
        Les ID des boutons sont calendar : (previousMonth, nextMonth, currentDate)
        :param to_json:
        :param to_mongo:
        :param to_Console:
        :param left:
        :return:
        """

        planning_link = self.driver.find_element_by_xpath('//a[contains(text(),"Plannings")]')
        planning_link.click()
        time.sleep(4)

        locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
        current_week_label = self.driver.find_element_by_id('calendar:currentWeek').text
        current_week_start = current_week_label.split('-')[0].strip() + " 2023"
        current_week_start = datetime.strptime(current_week_start, '%d %B %Y')

        start_date = datetime(current_week_start.year, 1, 1) if startOfTheYear else current_week_start
        end_date = datetime(current_week_start.year, 8, 31) if not startOfTheYear else current_week_start

        num_weeks = util.week_difference(start_date, end_date)
        for _ in range(num_weeks):
            self.logger.info('Weeks left: ' + str(num_weeks - _))

            if startOfTheYear:
                navigation_button = self.driver.find_element_by_id('calendar:previousMonth')
            else:
                navigation_button = self.driver.find_element_by_id('calendar:nextMonth')

            navigation_button.click()
            time.sleep(10)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            div = soup.find('div', id='calendar:myschedule')

            thead = soup.find('thead')
            joursDeLaSemaine = su.get_jours_de_la_semaine(thead)

            formated_date = joursDeLaSemaine.get("Lundi").replace('/', '_')

            if not util.compare_html(div, "data/out/html/schedule_du_{}.html".format(formated_date)):
                util.write_html(div, "data/out/html/schedule_du_{}.html".format(formated_date))
            else:
                continue

            time.sleep(10)
            px_day = su.get_event_lefts(soup, "fc-event")
            px_week = su.get_jours_par_position(soup, "fc-event")

            px_to_weekday = {str(px): weekday for weekday, px in px_week.items()}

            final_dict = {}

            if not px_day:
                weekday = joursDeLaSemaine.get(px_to_weekday.get(px_day[0])) if px_day else None
                if weekday is None:
                    weekday = formated_date
                su.write_to_json(final_dict,
                                 f"out/semaine_du_{weekday.replace('/', '_')}.json")
                continue

            px_day_without_duplicates = list(dict.fromkeys(px_day))

            for i in range(len(px_day_without_duplicates)):
                if px_day[i] is None:
                    px_day[i] = px_day_without_duplicates[i]

            event_titles, event_times = su.get_event_data(soup)
            combined = su.get_combined_data(event_times, event_titles, px_day)

            final_dict = su.build_final_dict(self.driver, combined, px_to_weekday, joursDeLaSemaine)
            final_dict = su.sort_final_dict(final_dict)

            if to_json:
                su.write_to_json(final_dict, "out/semaine_du_{}.json".format(formated_date))

            if to_mongo:
                # su.write_to_mongo(final_dict) # TODO: not implemented yet
                pass

            if to_Console:
                # TODO: not done yet
                print(final_dict)
                # util.write_to_console(final_dict)
