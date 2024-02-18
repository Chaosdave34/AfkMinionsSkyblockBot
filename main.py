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

mode = "starting"


@Once(bot, "spawn")
def on_spawn(*args):
    utils.init(bot, config["key"])

    print("[Bot] Joined Hypixel")
    bot.waitForTicks(60)
    bot.chat("/skyblock")


@On(bot, "message")
def on_message(*args):
    global mode

    if args[2] == "chat":
        text = utils.compile_text(args[1])

        if mode == "starting":
            if "Welcome to Hypixel SkyBlock!" in text:
                mode = "skyblock"
                print("[Bot] Joined Skyblock!")

        elif mode == "skyblock":
            if utils.get_location() == "Your Island":
                print("[Bot] You are on your Island!")
                mode = "home"

                print(f"[Bot] Active PEt: {utils.get_active_pet()}")

            else:
                print("[Bot] You are not on your Island, warping...")
                bot.chat("/warp home")
                bot.waitForTicks(20)
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

            # Filter
            if "[Important]" in text:
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


@On(bot, "error")
def on_error(*args):
    print("[Bot] Error!")


@On(bot, "kick")
def on_kick(*args):
    print(f"[Bot] Kick!")
