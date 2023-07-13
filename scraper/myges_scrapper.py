import locale
from datetime import datetime
import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from scraper.selenium_utils import wait_for_element

from utils import schedule_utils as su
from utils import logger_utils as log
from utils import global_utils as util
from utils import directory_utils as du
from utils.global_utils import write_to_json


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

    def get_schedule(self, to_json=True, to_mongo=False, to_Console=False, startOfTheYear=False, endOfTheYear=False,
                     date_string="17_07_23"):
        """
        Récupère le planning de l'utilisateur
        Les ID des boutons sont calendar : (previousMonth, nextMonth, currentDate)
        :param to_json:
        :param to_mongo:
        :param to_Console:
        :param left:
        :return:
        """

        # TODO, on load une seule fois sur le startOfTheYear (quand on a pas chargé les json), sinon on parcourt le endOfTheYear en le passant en False
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

        if startOfTheYear:
            current_week_start_string = current_week_start.strftime("%d_%m_%y")
            if not util.check_existing_json_files_for_week_range(current_week_start.year, 1, current_week_start_string):
                self.logger.info('No json files found, starting scraping')
            else:
                self.logger.info('Json files found, skipping scraping for the start of the year')
                return

        if date_string:
            target_date = datetime.strptime(date_string, "%d_%m_%y")
            weeks_diff = util.week_difference(current_week_start, target_date)

            log.get_logger().info('Weeks diff: ' + str(weeks_diff))
            log.get_logger().info('Target date: ' + target_date.strftime("%d_%m_%y"))
            log.get_logger().info('Current week start: ' + current_week_start.strftime("%d_%m_%y"))

            if weeks_diff > 0:
                navigation_button = self.driver.find_element_by_id('calendar:nextMonth')
                for _ in range(weeks_diff):
                    navigation_button.click()
                    time.sleep(10)
            elif weeks_diff < 0:
                navigation_button = self.driver.find_element_by_id('calendar:previousMonth')
                for _ in range(abs(weeks_diff)):
                    navigation_button.click()
                    time.sleep(10)

            num_weeks = weeks_diff

        for _ in range(num_weeks):
            self.logger.info('Weeks left: ' + str(num_weeks - _))

            if startOfTheYear:
                navigation_button = self.driver.find_element_by_id('calendar:previousMonth')
            elif endOfTheYear:
                navigation_button = self.driver.find_element_by_id('calendar:nextMonth')

            if _ > 0:
                navigation_button.click()
                time.sleep(10)
            elif endOfTheYear:
                log.get_logger().info('First week, skipping navigation')
            elif date_string == current_week_start.strftime("%d_%m_%y"):
                log.get_logger().info('First week, skipping navigation')

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
                                 f"semaine_du_{weekday.replace('/', '_')}.json", directory="schedule")
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
                su.write_to_json(final_dict, "semaine_du_{}.json".format(formated_date), directory="schedule")

            if to_mongo:
                # su.write_to_mongo(final_dict) # TODO: not implemented yet
                pass

            if to_Console:
                # TODO: not done yet
                print(final_dict)
                # util.write_to_console(final_dict)

        return final_dict

    def get_students_directory(self):
        self.driver.get('https://myges.fr/student/student-directory')

        active_button = wait_for_element(self.driver, By.CSS_SELECTOR, 'div.ui-state-active')

        arr = du.get_current_directory(self.driver)
        write_to_json({"students": arr}, 'directory/3AL2_2s.json')

        al_button = wait_for_element(self.driver, By.CSS_SELECTOR,
                                     '#puidOptions > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(3) > div:nth-child(1) > div:nth-child(2)')
        al_button.click()

        arr = du.get_current_directory(self.driver)
        write_to_json({"students": arr}, 'directory/3AL_2s.json')

        y3_button = wait_for_element(self.driver, By.CSS_SELECTOR,
                                     '#puidOptions > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(5) > div:nth-child(1) > div:nth-child(2)')
        y3_button.click()

        arr = du.get_current_directory(self.driver)
        write_to_json({"students": arr}, 'directory/3ESGI_2s.json')

        unfold_button = wait_for_element(self.driver, By.CSS_SELECTOR, '.ui-selectonemenu-trigger')
        unfold_button.click()
        grade4_select = wait_for_element(self.driver, By.CSS_SELECTOR, 'li.ui-selectonemenu-item:nth-child(1)')
        grade4_select.click()

        arr = du.get_current_directory(self.driver)
        write_to_json({"students": arr}, 'directory/4AL.json')

        y4_button = wait_for_element(self.driver, By.CSS_SELECTOR,
                                     '#puidOptions > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(5) > div:nth-child(1) > div:nth-child(2)')
        y4_button.click()

        arr = du.get_current_directory(self.driver)
        write_to_json({"students": arr}, 'directory/4ESGI.json')

        unfold_button = wait_for_element(self.driver, By.CSS_SELECTOR, '.ui-selectonemenu-trigger')
        unfold_button.click()
        grade3_select = wait_for_element(self.driver, By.CSS_SELECTOR, 'li.ui-selectonemenu-item:nth-child(3)')
        grade3_select.click()

        arr = du.get_current_directory(self.driver)
        write_to_json({"students": arr}, 'directory/3AL2_1s.json')

        al_button = wait_for_element(self.driver, By.CSS_SELECTOR,
                                     '#puidOptions > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(3) > div:nth-child(1) > div:nth-child(2)')
        al_button.click()

        arr = du.get_current_directory(self.driver)
        write_to_json({"students": arr}, 'directory/3AL_1s.json')

        y3_button = wait_for_element(self.driver, By.CSS_SELECTOR,
                                     '#puidOptions > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(5) > div:nth-child(1) > div:nth-child(2)')
        y3_button.click()

        arr = du.get_current_directory(self.driver)
        write_to_json({"students": arr}, 'directory/3ESGI_1s.json')
