import enum

from javascript import require, On, Once
import utils

mineflayer = require("mineflayer")

config = utils.read_config()

bot = mineflayer.createBot({
    "host": "hypixel.net",
    "username": config["email"],
    "auth": "microsoft",
    "version": "1.8.9"
})

utils = utils.Utils()


class Mode(enum.Enum):
    STARTING = 1
    SKYBLOCK = 2
    HOME = 3


mode = Mode.STARTING

filter_list = [
    "Mining Speed Boost",
    "Guild >",
    "Friend >",
    "✆",
    "Watchdog",
    "WATCHDOG",
    "Staff have banned",
    "Blacklisted modifications"
]


@Once(bot, "spawn")
def on_spawn(*_args):
    utils.init(bot, config["key"])

    print("[Bot] Joined Hypixel")

    bot.waitForTicks(60)
    bot.chat("/skyblock")


@On(bot, "message")
def on_message(*args):
    global mode

    if args[2] == "chat":
        text = utils.compile_text(args[1])

        if mode == Mode.STARTING:
            if "Welcome to Hypixel SkyBlock!" in text:
                print("[Bot] Joined Skyblock!")
                mode = Mode.SKYBLOCK

        elif mode == Mode.SKYBLOCK:
            if utils.get_location() == "Your Island":
                print("[Bot] You are on your Island!")
                mode = Mode.HOME

            else:
                print("[Bot] You are not on your Island, warping...")
                bot.waitForTicks(20)
                bot.chat("/warp home")

        elif mode == Mode.HOME:
            if text == "":
                return
            elif any([x in text for x in filter_list]):
                return

            # Filter
            if "[Important]" in text:
                print(text)

            elif "to warp out" in text:
                print(f"[Important] {text}")

            elif "Evacuating to Hub..." in text:
                mode = Mode.SKYBLOCK
                bot.waitForTicks(60)

            elif "A disconnect occured" in text:
                bot.waitForTicks(60)
                bot.chat("/skyblock")

            elif "Out of sync" in text:
                bot.waitForTicks(60)
                bot.chat("/lobby")
                bot.waitForTicks(60)
                bot.chat("/skyblock")
                mode = Mode.SKYBLOCK
            else:
                print(f"[Chat] {text}")


@On(bot, "error")
def on_error(*_args):
    print("[Bot] Error!")


@On(bot, "kick")
def on_kick(*_args):
    print(f"[Bot] Kick!")
