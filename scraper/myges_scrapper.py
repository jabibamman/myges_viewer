from datetime import datetime
import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper.selenium_utils import wait_for_element

from utils.logger_utils import get_logger
from utils.schedule_utils import get_jours_de_la_semaine_json, get_jours_de_la_semaine


class MyGesScraper:
    logger = get_logger()

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


    def get_schedule(self):
        planning_link = self.driver.find_element_by_xpath('//a[contains(text(),"Plannings")]')
        planning_link.click()
        time.sleep(4)

        previousMonth = self.driver.find_element_by_id('calendar:previousMonth')
        nextMonth = self.driver.find_element_by_id('calendar:nextMonth')
        currentMonth = self.driver.find_element_by_id('calendar:currentDate')

        previousMonth.click()
        time.sleep(4)

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        div = soup.find('div', id='calendar:myschedule')
        thead = soup.find('thead')

        get_jours_de_la_semaine_json(thead)

        joursDeLaSemaine = get_jours_de_la_semaine(thead)

        event_titles = [tag.text for tag in div.find_all(class_="fc-event-title")]
        event_times = [tag.text for tag in div.find_all(class_="fc-event-time")]

        combined = list(zip(event_times, event_titles))  # tuples (time, title)

        current_date_index = 0

        with open("data/semaine_de_cours.json", "w") as f:
            f.write(joursDeLaSemaine[current_date_index] + '\n')
            end_time_previous = datetime.strptime('00:00',
                                                  "%H:%M")  # initialization with a time guaranteed to be earlier

            for i in range(len(combined)):
                start_time_current, end_time_current = [datetime.strptime(t.strip(), "%H:%M") for t in
                                                        combined[i][0].split('-')]
                if start_time_current < end_time_previous:
                    current_date_index += 1
                    if current_date_index >= len(joursDeLaSemaine):  # prevent index out of range error
                        break
                    f.write(joursDeLaSemaine[current_date_index] + '\n')

                f.write(combined[i][0] + ' ' + combined[i][1] + '\n')

                end_time_previous = end_time_current
