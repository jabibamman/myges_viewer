from interfaces.api import app
from scraper import initialise_selenium, MyGesScraper
from utils.config_utils import read_config

if __name__ == '__main__':
    # app.run(debug=True)

    username, password = read_config()
    driver = initialise_selenium()
    scraper = MyGesScraper(driver, username, password)

    scraper.login()
    directory = scraper.get_teachers_directory()

    driver.quit()
