import asyncio
import threading
import discord
from flask import Flask

from interfaces.api import app
from interfaces.discord_bot import MyBot
from utils.config_utils import username, password, secret_discord
from scraper.myges_scrapper import MyGesScraper
from scraper.selenium_utils import initialise_selenium
from utils import logger_utils as log

async def get_marks_periodicly(bot):
    
    logger = log.get_logger()

    while True:
        driver = initialise_selenium(headless=True)
        scraper = MyGesScraper(driver, username, password)
        login = scraper.login()
        if login:
            await scraper.get_lessons_periodicly("2022-2023", "1", bot=bot)
            await scraper.get_marks_periodicly("2022-2023", "1", bot=bot)
        else:
            logger.error("Login failed")
        await asyncio.sleep(300)

async def get_schedule_periodicly(bot):
    logger = log.get_logger()

    while True:
        driver = initialise_selenium(headless=False)
        scraper = MyGesScraper(driver, username, password)
        login = scraper.login()
        if login:
            schedule = await scraper.get_schedule(startOfTheYear=False, date_string="17_07_23",bot=bot)
            if 404 in schedule :
                logger.error("Schedule not found")


        else:
            logger.error("Login failed")
        await asyncio.sleep(300)

async def bot_and_scraper():
    bot_token = secret_discord
    intents = discord.Intents.default()
    intents.message_content = True
    bot = MyBot(command_prefix='!', intents=intents)
    asyncio.create_task(get_marks_periodicly(bot))
    await bot.start(bot_token)

def run_bot_and_scraper():
    asyncio.run(bot_and_scraper())

if __name__ == '__main__':
    t1 = threading.Thread(target=run_bot_and_scraper)
    t1.start()

    app.run(debug=True)
