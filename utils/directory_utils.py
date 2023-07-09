import logging
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from scraper.selenium_utils import wait_for_element


def get_current_directory(driver):
    i = 0
    while True:
        exist = wait_for_element(driver, By.ID, f'studentDirectoryWidget:studentDirectoryDataGrid:{i}:name', 1)
        if not exist:
            next = wait_for_element(driver, By.CSS_SELECTOR, '#studentDirectoryWidget\:studentDirectoryDataGrid_paginator_top > span:nth-child(4)')
            logging.getLogger('logger').debug("CHANGING PAGE")
            next.click()

        photo = wait_for_element(driver, By.ID, f'studentDirectoryWidget:studentDirectoryDataGrid:{i}:j_idt180')
        if not photo:
            break
        name = wait_for_element(driver, By.ID, f'studentDirectoryWidget:studentDirectoryDataGrid:{i}:name')
        try:
            name_text = name.text
            if not name_text:
                break
            logging.getLogger('logger').debug(str(i)+" - "+photo.get_attribute("src")+" - "+name_text.replace("\n", " "))
        except StaleElementReferenceException:
            logging.getLogger('logger').error("StaleElementReferenceException occurred for name element")
        i += 1
