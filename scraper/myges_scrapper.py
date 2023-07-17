import json
import locale
from datetime import datetime
import re
import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from scraper.selenium_utils import wait_for_element

from utils import schedule_utils as su
from utils import marks_utils as mu
from utils import logger_utils as log
from utils import global_utils as util
from utils.config_utils import discord_channel


def compare_tabs(array1, array2):
    if len(array1) != len(array2):
        print("Les tableaux ne font pas la même taille")
        return False, []

    obj_diff = []
    for i, (obj1, obj2) in enumerate(zip(array1, array2)):
        if obj1 != obj2:
            obj_diff.append(obj1)

    return not bool(obj_diff), obj_diff


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

    def get_schedule(self, to_json=True, to_Console=False, startOfTheYear=False, endOfTheYear=False,
                     date_string=None,bot=None):
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
        final_dict = {}

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
                self.logger.info('Start of the year already scraped, skipping')
                return

        if date_string is not None:
            self.logger.info('Date string is not empty, scraping only one week')
            target_date = datetime.strptime(date_string, "%d_%m_%y").replace(hour=0, minute=0, second=0)
            print(current_week_start)
            current_week_start = current_week_start.replace(hour=0, minute=0, second=0)
            weeks_diff = util.week_difference(current_week_start, target_date)

            if current_week_start.weekday() == 6:  # Sunday
                weeks_diff += 1 if weeks_diff < 0 else -1


            log.get_logger().info('Weeks diff: ' + str(weeks_diff))
            log.get_logger().info('Target date: ' + target_date.strftime("%d_%m_%y"))
            log.get_logger().info('Current week start: ' + current_week_start.strftime("%d_%m_%y"))

            if target_date.strftime("%d_%m_%y") == current_week_start.strftime("%d_%m_%y"):
                is_same_week = True
                num_weeks = 1

            if weeks_diff != 0:
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

            self.logger.debug('px_day: ' + str(px_day))
            px_to_weekday = {str(px): weekday for weekday, px in px_week.items()}

            self.logger.debug('px_to_weekday: ' + str(px_to_weekday))

            final_dict = {}

            if not px_day:
                weekday = joursDeLaSemaine.get(px_to_weekday.get(px_day[0])) if px_day else None
                if weekday is None:
                    weekday = formated_date
                su.write_to_json(final_dict,
                                 f"semaine_du_{weekday.replace('/', '_')}.json", directory="schedule")
                continue

            px_day_without_duplicates = list(dict.fromkeys(px_day))

            self.logger.debug('px_day_without_duplicates: ' + str(px_day_without_duplicates))

            for i in range(len(px_day_without_duplicates)):
                if px_day[i] is None:
                    px_day[i] = px_day_without_duplicates[i]

            event_titles, event_times = su.get_event_data(soup)
            combined = su.get_combined_data(event_times, event_titles, px_day)

            final_dict = su.build_final_dict(self.driver, combined, px_to_weekday, joursDeLaSemaine)

            final_dict = su.sort_final_dict(final_dict)

            if to_json:
                su.write_to_json(final_dict, "semaine_du_{}.json".format(formated_date), directory="schedule")

            if to_Console:
                # TODO: not done yet
                print(final_dict)
                # util.write_to_console(final_dict)

        return final_dict

    def get_marks(self, year="2022-2023", semester="1"):
        """
        Récupère les notes de l'utilisateur en fonction d'une année et d'un semestre
        Renvoie toutes les dates du semestre
        Format "year" -> 2022-2023, 2021-2022, etc...
        Format "semester" -> 1 ou 2
        """

        self.driver.get('https://myges.fr/student/marks')

        time.sleep(5)

        label_element = wait_for_element(self.driver, By.ID, 'marksForm:j_idt174:periodSelect_label', 10)

        label_element.click()

        select_div = wait_for_element(self.driver, By.ID, 'marksForm:j_idt174:periodSelect_panel', 10)
        option_xpath = f'//li[contains(text(),"{year}") and contains(text(),"Semestre {semester}")]'
        option = select_div.find_element(By.XPATH, option_xpath)
        option.click()

        time.sleep(5)

        marks_table = wait_for_element(self.driver, By.ID, 'marksForm:marksWidget:coursesTable_data', 10)

        marks = []
        rows = marks_table.find_elements(By.TAG_NAME, 'tr')
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, 'td')
            class_name, teacher, coef, ects, cc1, cc2, cc3, exam = "", "", "", "", "", "", "", ""
            class_name = cells[0].text.strip()
            teacher = cells[1].text.strip()
            coef = cells[2].text.strip()
            ects = cells[3].text.strip()

            if len(cells) == 8:
                cc1 = cells[4].text.strip()
                cc2 = cells[5].text.strip()
                cc3 = cells[6].text.strip()
                exam = cells[7].text.strip()

            if len(cells) == 7:
                cc1 = cells[4].text.strip()
                cc2 = cells[5].text.strip()
                exam = cells[6].text.strip()

            if len(cells) == 6:
                cc1 = cells[4].text.strip()
                exam = cells[5].text.strip()

            if len(cells) == 5:
                exam = cells[4].text.strip()

            marks.append({
                'class_name': class_name,
                'teacher': teacher,
                'coef': coef,
                'ects': ects,
                'cc1': cc1,
                'cc2': cc2,
                'cc3': cc3,
                'exam': exam
            })

        mu.write_to_json(marks, "marks_{}.json".format(year + "_semester_" + semester), directory="marks")
        return marks

    async def get_marks_periodicly(self, year="2022-2023", semester="1", bot=None):
        """
        Récupère les notes de l'utilisateur actuel
        Compare avec le fichier json actuel et remplace si différent et notifie l'utilisateur
        Format "year" -> 2022-2023, 2021-2022, etc...
        Format "semester" -> 1 ou 2
        """

        if bot is None:
            self.logger.error("Bot is not defined")
            return

        self.driver.get('https://myges.fr/student/marks')

        time.sleep(5)
        label_element = wait_for_element(self.driver, By.ID, 'marksForm:j_idt174:periodSelect_label', 10)

        label_element.click()

        select_div = wait_for_element(self.driver, By.ID, 'marksForm:j_idt174:periodSelect_panel', 10)
        option_xpath = f'//li[contains(text(),"{year}") and contains(text(),"Semestre {semester}")]'
        option = select_div.find_element(By.XPATH, option_xpath)
        option.click()

        time.sleep(5)

        marks_table = wait_for_element(self.driver, By.ID, 'marksForm:marksWidget:coursesTable_data', 10)

        marks = []
        rows = marks_table.find_elements(By.TAG_NAME, 'tr')
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, 'td')

            class_name, teacher, coef, ects, cc1, cc2, cc3, exam = "", "", "", "", "", "", "", ""
            class_name = cells[0].text.strip()
            teacher = cells[1].text.strip()
            coef = cells[2].text.strip()
            ects = cells[3].text.strip()

            if len(cells) == 8:
                cc1 = cells[4].text.strip()
                cc2 = cells[5].text.strip()
                cc3 = cells[6].text.strip()
                exam = cells[7].text.strip()

            if len(cells) == 7:
                cc1 = cells[4].text.strip()
                cc2 = cells[5].text.strip()
                exam = cells[6].text.strip()

            if len(cells) == 6:
                cc1 = cells[4].text.strip()
                exam = cells[5].text.strip()

            if len(cells) == 5:
                exam = cells[4].text.strip()

            marks.append({
                'class_name': class_name,
                'teacher': teacher,
                'coef': coef,
                'ects': ects,
                'cc1': cc1,
                'cc2': cc2,
                'cc3': cc3,
                'exam': exam
            })

        json_marks = mu.get_marks_json(year, semester)

        if 404 in json_marks:
            self.get_marks(year, semester)
        else:
            is_equal, obj_diff = compare_tabs(marks, json_marks[0])

            if is_equal:
                self.logger.info("Les notes n'ont pas changés !")
            else:
                channel = await bot.fetch_channel(discord_channel)

                if channel is None:
                    self.logger.error("Channel not found")
                    return

                self.logger.info("Les notes suivantes ont changés !")

                for obj in obj_diff:
                    print("Vous avez une nouvelle note en '" + obj['class_name'] + "'")
                    await channel.send("Vous avez une nouvelle note en '" + obj['class_name'] + "'")

                    if obj['cc1'] != "":
                        self.logger.info("CC1 :", obj['cc1'])
                        await channel.send("CC1 :" + obj['cc1'])
                    if obj['cc2'] != "":
                        self.logger.info("CC2 :", obj['cc2'])
                        await channel.send("CC2 :" + obj['cc2'])

                    if obj['cc3'] != "":
                        self.logger.info("CC3 :", obj['cc3'])
                        await channel.send("CC3 :" + obj['cc3'])

                    if obj['exam'] != "":
                        self.logger.info("Examen :", obj['exam'])
                        await channel.send("Examen :" + obj['exam'])

                mu.write_to_json(marks, "marks_{}.json".format(year + "_semester_" + semester), directory="marks")
        return marks
