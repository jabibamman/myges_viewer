import discord

from interfaces.api import app
from interfaces.discord_bot import MyBot

from scraper.myges_scrapper import MyGesScraper
from scraper.selenium_utils import initialise_selenium

from utils.config_utils import read_config, username, password, secret_discord

import sched
import time
import threading

def get_marks_periodicly():
    while True:
        driver = initialise_selenium(headless=False)
        print("Driver initialised")
        bot_token = secret_discord
        intents = discord.Intents.default()
        intents.message_content = True
        bot = MyBot(command_prefix='!', intents=intents)
    #    bot.run(bot_token)
        print("Bot started")
        scraper = MyGesScraper(driver, username, password)
        login = scraper.login()
        if login:
            print("Login successful")
            marks = scraper.get_marks_periodicly("2021-2022", "1", bot)
        else:
            print("Login failed")
        time.sleep(300)

if __name__ == '__main__':

    # Lancer la fonction en arrière-plan
    t = threading.Thread(target=get_marks_periodicly)
    t.daemon = True
    t.start()


    app.run(debug=True)
   # main()

