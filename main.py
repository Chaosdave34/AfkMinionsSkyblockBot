from javascript import require, On, Once
import time
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

prev_purse = ""
earned = 0

seconds = time.time()

prev_enchanted_sulphur = 0
prev_slime_balls = 0
prev_kills = 0

cap_hit_count = 0


@Once(bot, "spawn")
def on_spawn(*args):
    utils.init(bot, config["key"])

    print("[Bot] Joined Hypixel")
    bot.waitForTicks(60)
    bot.chat("/skyblock")


@On(bot, "teamUpdated")
def on_team_updated(*args):
    global mode, prev_purse, earned, seconds, prev_enchanted_sulphur, prev_slime_balls, prev_kills, cap_hit_count

    if mode == "home":
        if time.time() - seconds > config["timer_min"] * 60:
            purse = utils.get_purse()
            kills = utils.get_kill_count()
            sulphur = utils.get_sulphur_count()
            slime_balls = utils.get_enchanted_slime_ball_count()

            if prev_purse == "":
                print(f"[Info] Purse: {utils.format_coins(purse)}")
            else:
                profit = purse - prev_purse
                profit += (sulphur - prev_enchanted_sulphur) * 1600
                profit += (slime_balls - prev_slime_balls) * utils.get_enchanted_slime_ball_price()

                earned += int(profit)

                profit *= (3600 / (config["timer_min"] * 60))

                print(f"[Info] Purse: {utils.format_coins(purse)} coins | Kills: {kills - prev_kills} | Earned: {utils.format_coins(earned)} coins | "
                      f"Expected Profit: {utils.format_coins(round(profit))} coins | Slime cap hit {cap_hit_count} times")

            prev_purse = purse

            seconds = time.time()

            prev_enchanted_sulphur = sulphur
            prev_slime_balls = slime_balls
            prev_kills = kills

            cap_hit_count = 0


@On(bot, "message")
def on_message(*args):
    global mode, cap_hit_count

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
                bot.setQuickBarSlot(config["slot"] - 1)

                armor_pieces = utils.get_armor_piece_names()

                message = []

                if any([all([armor in x for x in armor_pieces])] for armor in ["Goldor", "Maxor", "Necron", "Storm", "Wither"]):
                    message.append("Correct Armor Set equipped!")
                else:
                    message.append("Wrong Armor Set equipped!")

                if "Daedalus Axe" in utils.get_selected_item_name():
                    message.append("Daedalus Axe selected!")
                else:
                    message.append("Daedalus Axe NOT selected!")

                message.append(f"Active Pet: {utils.get_active_pet()}")

                print("[Bot] " + " | ".join(message))

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
            if "You have reached the maximum number of Slimes allowed on your island." in text:
                cap_hit_count += 1
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


@On(bot, "error")
def on_error(*args):
    print("[Bot] Error!")


@On(bot, "kick")
def on_kick(*args):
    print(f"[Bot] Kick!")
