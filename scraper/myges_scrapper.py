import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper.selenium_utils import wait_for_element

from utils.logger_utils import get_logger

class MyGesScraper:
    logger = get_logger()
    def __init__(self, driver, username, password):
        self.driver = driver
        self.username = username
        self.password = password

    def login(self):
        self.driver.get('https://www.myges.fr/login')

        username_input = wait_for_element(self.driver, By.ID, 'username')
        password_input = wait_for_element(self.driver, By.ID, 'password')

        username_input.send_keys(self.username)
        password_input.send_keys(self.password)

        login_button = wait_for_element(self.driver, By.NAME, 'submit')
        login_button.click()

        time.sleep(5)
        if 'j_spring_cas_security_check' in self.driver.current_url:
            print('Login failed')
            return False
        else:
            self.logger.info('Login successful, current url is: ' + self.driver.current_url)
            time.sleep(5)
            return True
