from scraper.myges_scrapper import MyGesScraper
from scraper.selenium_utils import initialise_selenium
import json

with open('config.json') as f:
    config = json.load(f)
username = config['myges']['username']
password = config['myges']['password']

driver = initialise_selenium()

scraper = MyGesScraper(driver, username, password)

scraper.login()
driver.quit()
