from scraper.myges_scrapper import MyGesScraper
from scraper.selenium_utils import initialise_selenium

from utils.config_utils import read_config

username, password = read_config()
driver = initialise_selenium()
scraper = MyGesScraper(driver, username, password)

scraper.login()
driver.quit()
