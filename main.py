import os

from javascript import require, On, Once
import time
import yaml

mineflayer = require("mineflayer")

bot = mineflayer.createBot({
    "host": "hypixel.net",
    "username": "dfa-team@outlook.de",
    "auth": "microsoft",
    "version": "1.8.9"
})

if not os.path.isfile("config.yml"):
    with open("config.yml", "x") as writer:
        yaml.dump({"witherborn_count": 20, "slot": 8}, writer)

config = yaml.safe_load(open("config.yml"))

mode = "starting"
purse = ""
prev_purse = ""
witherborn_count = 0
seconds = 0
prev_enchanted_sulphur = 0
prev_kills = 0
earned = 0


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
        coins = coins[:length-3] + "," + coins[length-3:]

    if len(coins) > 7:
        coins = coins[:length-7] + "," + coins[length-7:]

    return coins


@Once(bot, "spawn")
def on_spawn(*args):
    print("Started!")
    print("[Bot] Joined Hypixel")


@On(bot, "message")
def on_message(*args):
    global mode, witherborn_count, seconds, prev_purse, prev_enchanted_sulphur, prev_kills, earned

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
                display_name = sidebar.itemsMap[item].displayName
                text = compile_text(display_name)
                if "⏣" in text:
                    if "Your Island" in text:
                        print("[Bot] You are on your Island!")
                        mode = "home"
                        bot.setQuickBarSlot(config["slot"] - 1)
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
                            kills = line.split(" ")[1].replace("§c", "")
                            kills = int(kills.replace(",", ""))

                if witherborn_count == config["witherborn_count"]:
                    if prev_purse == "":
                        print(f"[Info] Purse: {purse}")
                    else:
                        profit = (int(purse.replace(",", "")) - int(prev_purse.replace(",", ""))) * (3600 / (time.time() - seconds))
                        profit += ((sulphur - prev_enchanted_sulphur) * 1600) * (3600 / (time.time() - seconds))

                        earned += int(purse.replace(",", "")) - int(prev_purse.replace(",", "")) + (sulphur - prev_enchanted_sulphur) * 1600

                        print(f"[Info] Purse: {purse} coins | Kills: {kills - prev_kills} | Earned: {nice_coins(earned)} coins | "
                              f"Expected Profit: {nice_coins(round(profit))} coins")
                    witherborn_count = 0
                    prev_purse = purse
                    seconds = time.time()

                    prev_enchanted_sulphur = sulphur
                    prev_kills = kills

            elif "[Important]" in text:
                print(text)
            elif "to warp out" in text:
                print(f"[Important] {text}")
            elif "Evacuating to Hub..." in text:
                mode = "skyblock"
                bot.waitForTicks(60)
            else:
                print(f"[Chat] {text}")


@On(bot, "scoreUpdated")
def on_score_updated(*args):
    global purse
    if mode == "home":
        sidebar = bot.scoreboard.sidebar
        for item in sidebar.itemsMap:
            display_name = sidebar.itemsMap[item].displayName
            text = compile_text(display_name)
            if "Purse" in text:
                purse = text.split(" ")[1]
                break


@On(bot, "error")
def on_error(*args):
    print("[Bot] Error")


@On(bot, "kick")
def on_kick(*args):
    print(f"[Bot] Kick!")
