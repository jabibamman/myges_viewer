from interfaces.api import app

from scraper.myges_scrapper import MyGesScraper
from scraper.selenium_utils import initialise_selenium

from utils.config_utils import read_config, username, password

import sched
import time
import threading

def get_marks_periodicly():
    while True:
        driver = initialise_selenium()
        scraper = MyGesScraper(driver, username, password)
        login = scraper.login()

        if login:
            marks = scraper.get_marks_periodicly("2021-2022", "1")
        time.sleep(300)

if __name__ == '__main__':

    # Lancer la fonction en arrière-plan
    t = threading.Thread(target=get_marks_periodicly)
    t.daemon = True
    t.start()


    app.run(debug=True)

