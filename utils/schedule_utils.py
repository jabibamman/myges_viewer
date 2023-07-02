import json
from datetime import datetime
import re

from utils import json_utils as json


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
    jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

    jours_par_position = {jour: None for jour in jours}
    event_lefts = list(dict.fromkeys(get_event_lefts(soup, class_)))

    for jour in jours:

        if jours_par_position[jour] is None and event_lefts:
            jours_par_position[jour] = event_lefts.pop(0)

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


def build_final_dict(combined, px_to_weekday, joursDeLaSemaine):
    final_dict = {}
    for event_time, event_title, event_px in combined:
        day = f"{px_to_weekday.get(event_px)} - {joursDeLaSemaine.get(px_to_weekday.get(event_px))}"

        if day:
            if day not in final_dict:
                final_dict[day] = []
            final_dict[day].append({
                'name': event_title,
                'start': event_time.split('-')[0].strip(),
                'end': event_time.split('-')[1].strip(),
                'sizePX': event_px
            })

    return final_dict


def sort_final_dict(final_dict):
    for day in final_dict:
        final_dict[day] = sorted(final_dict[day], key=lambda x: x['start'])
    return final_dict


def write_to_json(final_dict, filename):
    with open(f"data/{filename}", "w") as f:
        json.dump(final_dict, f, indent=4)


