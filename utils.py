import os
import requests
import yaml


class Utils:
    def __init__(self):
        self.bot = None
        self.api_key = ""
        self.uuid = ""

    def init(self, bot, api_key):
        print("Started!")
        self.bot = bot
        self.api_key = api_key
        self.uuid = self.username_to_uuid(bot.player.username)

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

    @staticmethod
    def format_coins(coins) -> str:
        coins = str(coins)
        length = len(coins)

        if length > 3:
            coins = coins[:length - 3] + "," + coins[length - 3:]

        if len(coins) > 7:
            coins = coins[:length - 6] + "," + coins[length - 6:]

        return coins

    @staticmethod
    def username_to_uuid(username) -> str:
        response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        try:
            return response.json()["id"]
        except requests.exceptions.JSONDecodeError:
            return None

    def get_location(self) -> str:
        location = ""
        sidebar = self.bot.scoreboard.sidebar

        for item in sidebar.itemsMap:
            text = self.compile_text(sidebar.itemsMap[item].displayName)

            if "⏣" in text:
                location = text[3:]

        return location

    def get_purse(self) -> int:
        purse = 0
        sidebar = self.bot.scoreboard.sidebar
        for item in sidebar.itemsMap:
            text = self.compile_text(sidebar.itemsMap[item].displayName)
            if "Purse" in text:
                purse = text.split(" ")[1]
                purse = int(purse.replace(",", ""))
                break
        return purse

    def get_sulphur_count(self) -> int:
        sulphur = 0
        for item in self.bot.inventory.slots:
            if item is not None:
                if item.name == "glowstone_dust":
                    if "ench" in item.nbt.value:
                        sulphur += item.count
                elif item.name == "skull":
                    if "Enchanted Sulphur Cube" in item.nbt.value.display.value.Name.value:
                        sulphur += 160 * item.count
        return sulphur

    def get_kill_count(self) -> int:
        kills = 0
        inventory = self.bot.inventory
        selected = inventory.slots[inventory.hotbarStart + self.bot.quickBarSlot]
        if selected is not None:
            for line in selected.nbt.value.display.value.Lore.value.value:
                if "Kills:" in line:
                    kills = line.split(" ")[1].replace("§", "")
                    kills = int(kills.replace(",", ""))
        return kills

    def get_selected_item_name(self) -> str:
        inventory = self.bot.inventory
        selected = inventory.slots[inventory.hotbarStart + self.bot.quickBarSlot]
        if selected is not None:
            return selected.nbt.value.display.value.Name.value
        return "None"

    def get_armor_piece_names(self) -> tuple:
        armor_pieces = []
        for i in range(4):
            armor_pieces.append(self.bot.inventory.slots[i + 5].nbt.value.display.value.Name.value)
        return tuple(armor_pieces)

    def get_profile(self):
        response = requests.get("https://api.hypixel.net/skyblock/profiles", params={"key": self.api_key, "uuid": self.uuid})
        try:
            profiles = response.json()["profiles"]
            for profile in profiles:
                if profile["selected"]:
                    return profile
            return None
        except requests.exceptions.JSONDecodeError:
            return None

    def get_bazaar(self):
        response = requests.get("https://api.hypixel.net/skyblock/bazaar", params={"key": self.api_key})
        try:
            return response.json()["products"]
        except requests.exceptions.JSONDecodeError:
            return None

    def get_enchanted_slime_ball_count(self) -> int:
        profile = self.get_profile()

        if profile is not None:
            return profile["members"][self.uuid]["sacks_counts"]["ENCHANTED_SLIME_BALL"]
        return 0

    def get_enchanted_slime_ball_price(self) -> float:
        products = self.get_bazaar()
        if products is not None:
            return products["ENCHANTED_SLIME_BALL"]["quick_status"]["sellPrice"]
        return 0

    def get_active_pet(self) -> str:
        profile = self.get_profile()

        if profile is not None:
            pets = profile["members"][self.uuid]["pets"]

            for pet in pets:
                if pet["active"]:
                    return pet["type"]
        return "NONE"


def read_config() -> dict:
    if not os.path.isfile("config.yml"):
        with open("config.yml", "x") as writer:
            yaml.dump({"witherborn_count": 20, "slot": 8, "email": "", "key": ""}, writer)

    return yaml.safe_load(open("config.yml"))
