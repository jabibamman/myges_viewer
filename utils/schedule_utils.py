from datetime import datetime
import re

from utils.json_utils import write_to_json


def get_jours_de_la_semaine(thead):
    """Get schedule for the current week."""
    joursDeLaSemaine = re.findall(r'(\d{1,2})\/(\d{1,2})\/(\d{2})', str(thead))
    days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    joursDeLaSemaine = {days[datetime.strptime("/".join(jour), "%d/%m/%y").weekday()]: "/".join(jour) for jour in
                        joursDeLaSemaine}

    return joursDeLaSemaine


def get_jours_de_la_semaine_json(thead):
    """Get schedule for the current week."""
    joursDeLaSemaine = get_jours_de_la_semaine(thead)
    write_to_json(joursDeLaSemaine, "jours_de_la_semaine.json")
