from javascript import require, On, Once
import time

mineflayer = require("mineflayer")

bot = mineflayer.createBot({
    "host": "hypixel.net",
    "username": "dfa-team@outlook.de",
    "auth": "microsoft",
    "version": "1.8.9"
})
mode = "starting"
purse = ""
prev_purse = ""
witherborn_count = 0
witherborn_enemies = 0
seconds = 0
prev_enchanted_sulphur = 0


def compile_text(chat_message):
    text = chat_message["text"]
    if "extra" in chat_message:
        for extra in chat_message["extra"]:
            if not extra["reset"]:
                text += extra["text"]
            if "extra" in extra:
                for extra2 in extra["extra"]:
                    if not extra2["reset"]:
                        text += extra2["text"]
    return text


@Once(bot, "spawn")
def on_spawn(*args):
    print("Started!")
    print("[Bot] Joined Hypixel")


@On(bot, "message")
def on_message(*args):
    global mode, witherborn_count, witherborn_enemies, seconds, prev_purse, prev_enchanted_sulphur

    if args[2] == "chat":
        text = compile_text(args[1])

        if mode == "starting":
            if "Guild: Message Of The Day" in text:
                bot.chat("/skyblock")
            elif "Welcome to Hypixel SkyBlock!" in text:
                mode = "skyblock"
                print("[Bot] Joined Skyblock!")

        elif mode == "skyblock":
            sidebar = bot.scoreboard["sidebar"]
            for item in sidebar["itemsMap"]:
                display_name = sidebar["itemsMap"][item]["displayName"]
                text = compile_text(display_name)
                if "⏣" in text:
                    if "Your Island" in text:
                        print("[Bot] You are on your Island!")
                        mode = "home"
                        bot.setQuickBarSlot(7)
                    else:
                        if "Warping to your" not in text or "Warping..." not in text or "Sending to server" not in text:
                            print("[Bot] You are not on your Island, warping...")
                            bot.chat("/warp home")
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

            if "Witherborn" in text:
                count = text.split(" ")[3]
                witherborn_count += 1
                witherborn_enemies += int(count)
                slots = bot.inventory.slots
                sulphur = 0
                for item in slots:
                    if item is not None:
                        if item.name == "glowstone_dust":
                            if "ench" in item.nbt.value:
                                sulphur += item.count

                if witherborn_count == 20:
                    if prev_purse == "":
                        profit = 0
                    else:
                        profit = (int(purse.replace(",", "")) - int(prev_purse.replace(",", ""))) * (3600 / (time.time() - seconds))
                        profit += ((sulphur - prev_enchanted_sulphur) * 1600) * (3600 / (time.time() - seconds))

                    print(f"[Info] Purse: {purse} | Sulphur: {sulphur}| Witherborn: Hit {witherborn_enemies} Slimes | Expected Profit: {round(profit)}")
                    witherborn_enemies = 0
                    witherborn_count = 0
                    prev_purse = purse
                    seconds = time.time()

                    prev_enchanted_sulphur = sulphur
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
        sidebar = bot.scoreboard["sidebar"]
        for item in sidebar["itemsMap"]:
            display_name = sidebar["itemsMap"][item]["displayName"]
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
