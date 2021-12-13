import os

try:
    import dotenv
except ImportError:
    pass
else:
    dotenv.load_dotenv(".env")


class Config:
    def __init__(self):
        self.bot_token = os.environ["TOKEN"]
        self.bot_prefix = os.environ.get("PREFIX", ["ducc!", "d!"])
