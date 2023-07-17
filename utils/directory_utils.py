import logging
import os

from selenium.webdriver.common.by import By
from scraper.selenium_utils import wait_for_element
from utils.json_utils import load_json


def get_students_info(driver):
    arr = []
    i = 0
    while True:
        exist = wait_for_element(driver, By.ID, f'studentDirectoryWidget:studentDirectoryDataGrid:{i}:name', 1)
        if not exist:
            next = wait_for_element(driver, By.CSS_SELECTOR,
                                    '#studentDirectoryWidget\:studentDirectoryDataGrid_paginator_top > span:nth-child(4)')
            next.click()

        photo = wait_for_element(driver, By.ID, f'studentDirectoryWidget:studentDirectoryDataGrid:{i}:j_idt180')
        if not photo:
            return arr
        name = wait_for_element(driver, By.ID, f'studentDirectoryWidget:studentDirectoryDataGrid:{i}:name')
        if not name:
            return arr
        try:
            if not name.text:
                return arr
            arr.append({
                'name': name.text.replace("\n", " "),
                'photo': photo.get_attribute("src")
            })
        except:
            logging.getLogger('logger').error("StaleElementReferenceException occurred for name element")
        i += 1


def get_teachers_info(driver):
    arr = []
    i = 0
    while True:
        exist = wait_for_element(driver, By.ID, f'teacherTrombiWidget:teacherDirectoryDataGrid:{i}:name', 1)
        if not exist:
            next = wait_for_element(driver, By.CSS_SELECTOR, '#teacherTrombiWidget\:teacherDirectoryDataGrid_paginator_top > span:nth-child(4)')
            next.click()

        photo = wait_for_element(driver, By.ID, f'teacherTrombiWidget:teacherDirectoryDataGrid:{i}:j_idt176')
        if not photo:
            return arr
        name = wait_for_element(driver, By.ID, f'teacherTrombiWidget:teacherDirectoryDataGrid:{i}:name')
        if not name:
            return arr
        try:
            if not name.text:
                return arr
            arr.append({
                'name': name.text.replace("\n", " "),
                'photo': photo.get_attribute("src")
            })
        except:
            logging.getLogger('logger').error("StaleElementReferenceException occurred for name element")
        i += 1


def get_student_directory_json(year='3', promotion='ESGI', semester='1'):
    filename = f"data/directory/{year}{promotion}_{semester}s.json"
    if os.path.exists(filename):
        data = load_json(filename)
        return data, 200
    else:
        return {"error": "File does not exist"}, 404

def get_teacher_directory_json():
    filename = f"data/directory/teacher-2022-2023.json"
    if os.path.exists(filename):
        data = load_json(filename)
        return data, 200
    else:
        return {"error": "File does not exist"}, 404