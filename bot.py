import asyncio
import os
import time

import discord
from discord import Intents
from discord.ext import commands

from config import Config
from utils.database import Database


class DuccLife(commands.Bot):
    def __init__(self):
        self.config = Config()
        self.db = Database()
        intents = Intents.default()
        intents.members = True
        self._duckcoin = None
        super().__init__(
            command_prefix=self.config.bot_prefix,
            intents=intents,
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(
                everyone=False, users=True, roles=False
            ),
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="ducks race into the milky way!",
            ),
        )

        for file in os.listdir("cogs"):

            if file.endswith(".py") and not file.startswith("_"):

                name = file[:-3]
                self.load_extension(name=f"cogs.{name}")

        self.load_extension("jishaku")
        self.load_extension("autoreload")

    async def on_ready(self):
        print("Bot is ready.")

    @property
    def session(self):
        return self.http._HTTPClient__session

    def get_custom_emoji(self, name):
        emoji = discord.utils.get(self.emojis, name=name, guild__id=802477991624048670)
        return emoji or ""

    @property
    def duckcoin(self):
        self._duckcoin = self._duckcoin or self.get_custom_emoji("duckcoin")
        return self._duckcoin

    async def run_async(self, func, *args, **kwargs):
        return await self.loop.run_in_executor(None, func, *args, **kwargs)
