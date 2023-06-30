from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def initialise_selenium(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver


def wait_for_element(driver, by, value, delay=10):
    try:
        element = WebDriverWait(driver, delay).until(EC.presence_of_element_located((by, value)))
        return element
    except TimeoutException:
        print(f"Timeout waiting for element {value}")
        return None


def click_element(driver, by, value):
    try:
        element = wait_for_element(driver, by, value)
        if element is not None:
            ActionChains(driver).move_to_element(element).click(element).perform()
            return True
        return False
    except Exception as e:
        print(f"Error clicking element {value}: {str(e)}")
        return False


def get_element_text(driver, by, value):
    try:
        element = wait_for_element(driver, by, value)
        if element is not None:
            return element.text
        return None
    except Exception as e:
        print(f"Error getting text from element {value}: {str(e)}")
        return None


def get_element_attribute(driver, by, value, attribute):
    try:
        element = wait_for_element(driver, by, value)
        if element is not None:
            return element.get_attribute(attribute)
        return None
    except Exception as e:
        print(f"Error getting attribute {attribute} from element {value}: {str(e)}")
        return None


def get_element(driver, by, value):
    try:
        element = wait_for_element(driver, by, value)
        return element
    except Exception as e:
        print(f"Error getting element {value}: {str(e)}")
        return None
