import time
from datetime import datetime
import re

from selenium.common.exceptions import ElementClickInterceptedException

from scraper.selenium_utils import get_element_text, click_element
from utils import json_utils
from selenium.webdriver.common.by import By
from utils import logger_utils as log
from utils.global_utils import write_to_json


def get_jours_de_la_semaine(thead):
    """Get days of the week."""
    joursDeLaSemaine = re.findall(r'(\d{1,2})\/(\d{1,2})\/(\d{2})', str(thead))
    days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    joursDeLaSemaine = {days[datetime.strptime("/".join(jour), "%d/%m/%y").weekday()]: "/".join(jour) for jour in
                        joursDeLaSemaine}

    # logging.getLogger('logger').debug('Days of the week: ' + str(joursDeLaSemaine))
    return joursDeLaSemaine


def get_jours_de_la_semaine_json(thead):
    """Get days of the week and write them to a json file."""
    joursDeLaSemaine = get_jours_de_la_semaine(thead)
    write_to_json(joursDeLaSemaine, "jours_de_la_semaine.json")


def get_jours_par_position(soup, class_):
    """Get days position."""
    jours, position = json_utils.read_json_as_lists("jours_par_position.json")
    jours_avec_position = dict(zip(jours, position))
    event_lefts = list(dict.fromkeys(get_event_lefts(soup, class_)))
    jours_par_position = {}
    for jour, pos in jours_avec_position.items():
        if event_lefts and pos in event_lefts:
            jours_par_position[jour] = pos
            event_lefts.remove(pos)

    return jours_par_position


def get_event_lefts(soup, class_):
    """
    Get left styles for events
    useful for getting the position of the events on the calendar
    Tips :list(dict.fromkeys(event_lefts)) to remove duplicates
    :param soup:
    :param class_:
    :return: list of left(px) styles
    """

    events = soup.find_all('div', {'class': lambda x: x and x.startswith(class_)})
    event_lefts = []
    for event in events:
        style = event.get('style')
        if style:
            left_values = re.findall(r"left:\s*(\d+px)", style)
            if left_values:
                event_lefts.append(left_values[0])

    return event_lefts


def get_event_data(soup):
    div = soup.find('div', id='calendar:myschedule')

    event_titles = [tag.text for tag in div.find_all(class_="fc-event-title")]
    event_times = [tag.text for tag in div.find_all(class_="fc-event-time")]

    return event_titles, event_times


def get_combined_data(event_times, event_titles, px_day):
    return list(zip(event_times, event_titles, px_day))


def build_final_dict(driver, combined, px_to_weekday, joursDeLaSemaine):
    final_dict = {}
    for event_time, event_title, event_px in combined:
        matiere, duration, intervenant, salle, type, modality = get_course_details(driver, event_title, event_time,
                                                                                   event_px)
        if matiere == "" or intervenant == "":
            continue

        day = f"{px_to_weekday.get(event_px)} - {joursDeLaSemaine.get(px_to_weekday.get(event_px))}"
        if day:
            if day not in final_dict:
                final_dict[day] = []
            final_dict[day].append({
                'name': matiere,
                'intervenant': intervenant,
                'salle': salle,
                'start': event_time.split('-')[0].strip(),
                'end': event_time.split('-')[1].strip(),
                'type': type,
                'modality': modality,
                'commentaire': "",
                'sizePX': event_px
            })

    return final_dict


def get_px_from_day(day):
    jours_par_position = json_utils.read_json("jours_par_position.json")
    return jours_par_position.get(day)


def sort_final_dict(final_dict):
    for day in final_dict:
        final_dict[day] = sorted(final_dict[day], key=lambda x: x['start'])
    return final_dict


def get_course_details(driver, event_title, event_time, event_px):
    """Get course details."""
    events = driver.find_elements(By.XPATH,
                                  f"//div[starts-with(@class, 'fc-event') and contains(@style, 'left: {event_px};')]")
    for event in events:
        event_title_element = event.find_element(By.XPATH, ".//div[@class='fc-event-title']")
        if not event_title_element:
            continue
        if event_title_element.text.split('...', 1)[0] + '...' != event_title.split('...', 1)[0] + '...':
            continue

        event_time_element = event.find_element(By.XPATH, ".//div[@class='fc-event-time']")
        if not event_time_element:
            continue
        if event_time not in event_time_element.text:
            continue

        try:
            time.sleep(1)
            event.click()
        except ElementClickInterceptedException:
            elements = driver.find_elements_by_xpath("//*[starts-with(@id, 'j_idt17')]")
            matching_elements = [e for e in elements if re.match(r'j_idt17\d', e.get_attribute('id'))]

            if matching_elements:
                div = matching_elements[0]
                a = div.find_element(By.XPATH, ".//a")
            a.click()
            event.click()

        time.sleep(1)
        matiere = driver.find_element(By.XPATH, "//span[@id='matiere']")
        duration = driver.find_element(By.XPATH, "//span[@id='duration']")
        intervenant = driver.find_element(By.XPATH, "//span[@id='intervenant']")
        salle = driver.find_element(By.XPATH, "//span[@id='salle']")
        type = driver.find_element(By.XPATH, "//span[@id='type']")
        modality = driver.find_element(By.XPATH, "//span[@id='modality']")
        commentaire = driver.find_element(By.XPATH, "//span[@id='commentaire']")

        return matiere.text, duration.text, intervenant.text, salle.text, type.text, modality.text
    return "", "", "", "", "", ""
