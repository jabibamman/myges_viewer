import json
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

    def get_schedule(self, to_json=True, to_mongo=False, to_Console=False):
        """
        Récupère le planning de l'utilisateur
        Les ID des boutons sont calendar : (previousMonth, nextMonth, currentDate)
        :param to_json:
        :param to_mongo:
        :param to_Console:
        :return:
        """

        planning_link = self.driver.find_element_by_xpath('//a[contains(text(),"Plannings")]')
        planning_link.click()
        time.sleep(4)

        previousMonth = self.driver.find_element_by_id('calendar:previousMonth')
        previousMonth.click()
        time.sleep(10)

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        thead = soup.find('thead')

        joursDeLaSemaine = su.get_jours_de_la_semaine(thead)
        time.sleep(10)
        px_day = su.get_event_lefts(soup, "fc-event")
        px_week = su.get_jours_par_position(soup, "fc-event")

        px_day_without_duplicates = list(dict.fromkeys(px_day))

        for i in range(len(px_day_without_duplicates)):
            if px_day[i] is None:
                px_day[i] = px_day_without_duplicates[i]

        event_titles, event_times = su.get_event_data(soup)
        combined = su.get_combined_data(event_times, event_titles, px_day)

        px_to_weekday = {str(px): weekday for weekday, px in px_week.items()}

        final_dict = su.build_final_dict(self.driver, combined, px_to_weekday, joursDeLaSemaine)
        final_dict = su.sort_final_dict(final_dict)

        if to_json:
            su.write_to_json(final_dict,
                             f"semaine_du_{joursDeLaSemaine.get(px_to_weekday.get(px_day[0])).replace('/', '_')}.json")

        if to_mongo:
            # su.write_to_mongo(final_dict) # TODO: not implemented yet
            pass

        if to_Console:
            # TODO: not done yet
            print(final_dict)
            #util.write_to_console(final_dict)



