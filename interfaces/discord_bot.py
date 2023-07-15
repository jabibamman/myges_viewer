import discord
from discord.ext import commands
from utils.config_utils import secret_discord


class MyBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents)
        self.add_commands()

    def add_commands(self):
        @self.command(name='test')
        async def test(ctx, arg):
            await ctx.channel.send(arg)
    async def on_ready(self):
        print(f'We have logged in as {self.user}')
        channel = self.get_channel(1029086619002732629)
        await channel.send('hi')


def main():
    bot_token = secret_discord

    intents = discord.Intents.default()
    intents.message_content = True
    bot = MyBot(command_prefix='!', intents=intents)
    bot.run(bot_token)


