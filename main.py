import os

from bot import DuccLife

os.environ.setdefault("JISHAKU_HIDE", "1")
os.environ.setdefault("JISHAKU_NO_UNDERSCORE", "1")

bot = DuccLife()

if __name__ == "__main__":

    bot.run(bot.config.bot_token)
