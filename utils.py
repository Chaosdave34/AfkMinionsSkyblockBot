import os
import requests
import yaml


class Utils:
    def __init__(self):
        self.bot = None

    def init(self, bot):
        print("Started!")
        self.bot = bot

    @staticmethod
    def compile_text(chat_message) -> str:
        text = chat_message.text
        if "extra" in chat_message:
            for extra in chat_message.extra:
                if not extra.reset:
                    text += extra.text
                if "extra" in extra:
                    for extra2 in extra.extra:
                        if not extra2.reset:
                            text += extra2.text
        return text

    def get_location(self) -> str:
        location = ""
        sidebar = self.bot.scoreboard.sidebar

        for item in sidebar.itemsMap:
            text = self.compile_text(sidebar.itemsMap[item].displayName)

            if "⏣" in text:
                location = text[3:]

        return location


def read_config() -> dict:
    if not os.path.isfile("config.yml"):
        with open("config.yml", "x") as writer:
            yaml.dump({"email": ""}, writer)

    return yaml.safe_load(open("config.yml"))
