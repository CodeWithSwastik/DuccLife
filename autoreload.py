import asyncio
import os
import traceback

from discord.ext.commands import Bot, Cog
from watchgod import awatch
from watchgod.watcher import Change


class UnloadException(Exception):
    pass


class AutoReloader(Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.coro = self.reloader()
        self.task = asyncio.ensure_future(self.coro)

    def cog_unload(self) -> None:
        self.coro.throw(UnloadException())

    async def reloader(self):
        try:
            async for changes in awatch("cogs" + os.path.sep):
                for change_type, path in changes:
                    if not path.endswith(".py"):
                        print(f"Skipping {path} as it doesn't end with .py")
                        continue
                    if path.count(".") != 1:
                        print(
                            f"Skipping {path} as it has more than one '.' in it's name"
                        )
                        continue
                    ext = path.replace(os.path.sep, ".")[:-3]
                    if change_type == Change.modified:
                        if ext in self.bot.extensions:
                            self.bot.unload_extension(ext)
                        self.load(ext)
                    elif change_type == Change.added:
                        self.load(ext)
                    elif change_type == Change.deleted and ext in self.bot.extensions:
                        self.bot.unload_extension(ext)
        except UnloadException:
            return

    def load(self, ext: str):
        try:
            self.bot.load_extension(ext)
        except Exception:
            print(f"Failed to load extension {ext}")
            traceback.print_exc()
        else:
            print(f"Loaded extension {ext}")


def setup(bot: Bot):
    bot.add_cog(AutoReloader(bot))