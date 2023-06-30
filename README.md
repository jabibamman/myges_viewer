# MyGes Viewer

## Description

Ce projet consiste en un programme qui extrait les données du site MyGes, les sauvegarde dans un format approprié (JSON, iCal) et fournit un accès à ces données via diverses interfaces (CLI, GUI, API Web, Discord Bot). 

## Fonctionnalités supplémentaires 

- Ajout automatique de l'emploi du temps à votre Google Calendar.
- Envoi d'un e-mail en cas de nouvelles notes disponibles.

## Installation

Pour installer et utiliser ce projet, vous aurez besoin de Python 3.8 ou supérieur.

1. Clonez ce dépôt sur votre machine locale.

```sh
git clone https://github.com/jabibamman/myges_viewer.git
cd myges_viewer
```

1. Installez les dépendances.
    
```sh
pip install -r requirements.txt
```
   
1. Configurez le fichier `config.json` avec vos identifiants MyGes et vos préférences.

```json
{
  "myges": {
    "username": "votre_identifiant",
    "password": "votre_mot_de_passe"
  }
} 
```

## Utilisation
Pour exécuter le programme, utilisez la commande suivante :
    
 ```sh
 python main.py
 ```

## Tests
Pour exécuter les tests, utilisez la commande suivante :
        
```sh
pytest tests/
```

## Contribuer
Vos contributions sont les bienvenues ! Pour contribuer à ce projet, veuillez forker le dépôt, effectuer vos modifications et soumettre une Pull Request.

## Licence
Ce projet ne contient pas de licence. Vous êtes libre de l'utiliser et de le modifier comme bon vous semble.