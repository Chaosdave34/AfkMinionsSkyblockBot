import os

from javascript import require, On, Once
import time
import yaml
import requests

mineflayer = require("mineflayer")

if not os.path.isfile("config.yml"):
    with open("config.yml", "x") as writer:
        yaml.dump({"witherborn_count": 20, "slot": 8, "email": "", "key": ""}, writer)

config = yaml.safe_load(open("config.yml"))

bot = mineflayer.createBot({
    "host": "hypixel.net",
    "username": config["email"],
    "auth": "microsoft",
    "version": "1.8.9"
})

mode = "starting"

purse = ""
prev_purse = ""
earned = 0

witherborn_count = 0
seconds = 0

prev_enchanted_sulphur = 0
prev_slime_balls = 0
prev_kills = 0


def compile_text(chat_message):
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


def nice_coins(coins):
    coins = str(coins)
    length = len(coins)
    if length > 3:
        coins = coins[:length - 3] + "," + coins[length - 3:]

    if len(coins) > 7:
        coins = coins[:length - 6] + "," + coins[length - 6:]

    return coins


def get_profiles():
    response = requests.get("https://api.hypixel.net/skyblock/profiles", params={"key": config["key"], "uuid": username_to_uuid(bot.player.username)})
    try:
        return response.json()["profiles"]
    except requests.exceptions.JSONDecodeError:
        return None


def get_bazaar():
    response = requests.get("https://api.hypixel.net/skyblock/bazaar", params={"key": config["key"]})
    try:
        return response.json()["products"]
    except requests.exceptions.JSONDecodeError:
        return None


def get_slime_balls():
    profiles = get_profiles()

    if profiles is not None:
        for profile in profiles:
            if profile["selected"]:
                return profile["members"][username_to_uuid(bot.player.username)]["sacks_counts"]["ENCHANTED_SLIME_BALL"]
    return 0


def get_slime_ball_prices():
    products = get_bazaar()
    if products is not None:
        return products["ENCHANTED_SLIME_BALL"]["quick_status"]["sellPrice"]
    return 0

def get_active_pet():
    profiles = get_profiles()

    if profiles is not None:
        for profile in profiles:
            if profile["selected"]:
                pets = profile["members"][username_to_uuid(bot.player.username)]["pets"]

                for pet in pets:
                    if pet["active"]:
                        return pet["type"]
    return "NONE"


def username_to_uuid(username):
    response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
    try:
        return response.json()["id"]
    except requests.exceptions.JSONDecodeError:
        return None


@Once(bot, "spawn")
def on_spawn(*args):
    print("Started!")
    print("[Bot] Joined Hypixel")


@On(bot, "message")
def on_message(*args):
    global mode, prev_purse, earned, witherborn_count, seconds, prev_enchanted_sulphur, prev_slime_balls, prev_kills

    if args[2] == "chat":
        text = compile_text(args[1])

        if mode == "starting":
            if "Guild: Message Of The Day" in text:
                bot.chat("/skyblock")
            elif "Welcome to Hypixel SkyBlock!" in text:
                mode = "skyblock"
                print("[Bot] Joined Skyblock!")

        elif mode == "skyblock":
            sidebar = bot.scoreboard.sidebar
            for item in sidebar.itemsMap:
                text = compile_text(sidebar.itemsMap[item].displayName)

                if "⏣" in text:
                    if "Your Island" in text:
                        print("[Bot] You are on your Island!")
                        mode = "home"
                        bot.setQuickBarSlot(config["slot"] - 1)

                        armor_pieces = []
                        for i in range(4):
                            armor_pieces.append(bot.inventory.slots[i + 5].nbt.value.display.value.Name.value)

                        if any([all([armor in x for x in armor_pieces])] for armor in ["Goldor", "Maxor", "Necron", "Storm", "Wither"]):
                            print("[Bot] Correct Armor Set equipped!")
                        else:
                            print("[Bot] Wrong Armor Set equipped!")
                        print(f"[Bot] Active Pet: {get_active_pet()}")

                    else:
                        print("[Bot] You are not on your Island, warping...")
                        bot.chat("/warp home")
                        bot.waitForTicks(20)
                    break
        elif mode == "home":
            if "Mining Speed Boost" in text:
                return
            if "Guild >" in text:
                return
            if "Friend >" in text:
                return
            if text == "":
                return
            if any([x in text for x in ["Watchdog", "WATCHDOG", "Staff have banned", "Blacklisted modifications"]]):
                return
            if "Teleport Pad" in text or "You fell into the void" in text:
                return

            if "Witherborn" in text:
                witherborn_count += 1

                slots = bot.inventory.slots
                sulphur = 0
                for item in slots:
                    if item is not None:
                        if item.name == "glowstone_dust":
                            if "ench" in item.nbt.value:
                                sulphur += item.count

                kills = 0
                if bot.inventory.slots[43] is not None:
                    for line in bot.inventory.slots[43].nbt.value.display.value.Lore.value.value:
                        if "Kills:" in line:
                            kills = line.split(" ")[1].replace("§", "")
                            kills = int(kills.replace(",", ""))

                if witherborn_count == config["witherborn_count"]:
                    slime_balls = get_slime_balls()

                    if prev_purse == "":
                        print(f"[Info] Purse: {purse}")
                    else:
                        profit = int(purse.replace(",", "")) - int(prev_purse.replace(",", ""))
                        profit += (sulphur - prev_enchanted_sulphur) * 1600
                        profit += (slime_balls - prev_slime_balls) * get_slime_ball_prices()

                        earned += int(profit)

                        profit *= 3600 / (time.time() - seconds)

                        print(f"[Info] Purse: {purse} coins | Kills: {kills - prev_kills} | Earned: {nice_coins(earned)} coins | "
                              f"Expected Profit: {nice_coins(round(profit))} coins")

                    prev_purse = purse

                    witherborn_count = 0
                    seconds = time.time()

                    prev_enchanted_sulphur = sulphur
                    prev_slime_balls = slime_balls
                    prev_kills = kills

            elif "[Important]" in text:
                print(text)
            elif "to warp out" in text:
                print(f"[Important] {text}")
            elif "Evacuating to Hub..." in text:
                mode = "skyblock"
                bot.waitForTicks(60)
            elif "A disconnect occured" in text:
                bot.waitForTicks(60)
                bot.chat("/skyblock")
            elif "Out of sync" in text:
                bot.waitForTicks(60)
                bot.chat("/lobby")
                bot.waitForTicks(60)
                bot.chat("/skyblock")
                mode = "starting"
            else:
                print(f"[Chat] {text}")


@On(bot, "scoreUpdated")
def on_score_updated(*args):
    global purse
    if mode == "home":
        sidebar = bot.scoreboard.sidebar
        for item in sidebar.itemsMap:
            text = compile_text(sidebar.itemsMap[item].displayName)
            if "Purse" in text:
                purse = text.split(" ")[1]
                break


@On(bot, "error")
def on_error(*args):
    print("[Bot] Error!")


@On(bot, "kick")
def on_kick(*args):
    print(f"[Bot] Kick!")
