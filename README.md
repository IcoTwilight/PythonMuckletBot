# PythonMuckletBot
A easy to use bot for the Mucklet engine.


## MuckletBot is a much more simple way to use the [original bot](https://github.com/ScientiFox/mucklet-bot-python) by [ScientiFox](https://github.com/ScientiFox)

There are 2 types of bots, UserBots and Bots
UserBots will require your Username and Password to be passed in as well as the bots name and surname you would like to controll
Bots only require the bots Token

### QuickStart:
```python3
import MuckletBot
import random, time

ACTIONS = [
    "Plays with a ball of yarn.",
    "Wipes her nose.",
    "Scratches her ear.",
    "Stretches, letting out a big yawn.",
    "Begins to fall asleep."
    ]

# this function is called when the bot receives a message that isn't part of the boot sequence
def OnMessage(bot, message):
    # if the message is for the bot (not any of your other awake characters) and not from the bot (to prevent infinite loops)
    if message.toSelf() and not message.fromSelf():
        # if the message is a message, address, or whisper
        if message.type() in ["address", "message", "whisper"]:
            # if the message is not empty
            if (text := message.message()) is not None:
                # if the message starts with "ping"
                if text.lower().startswith("ping"):
                    # send a message to the sender of the message (we know there is a sender because the type is either a address, message, or whisper)
                    bot.message(message.sender().id, "pong ^w^")
                # if the message starts with "inspect"
                elif text.lower().startswith("inspect"):
                    # send info about the message to the sender of the message
                    sendMessage = str(message)
                    bot.message(message.sender().id, sendMessage)
                else:
                    # otherwise, send the message back to the sender of the message
                    bot.message(message.sender().id, text)

# this function is called in a seperate thread when the bot is fully booted
def OnStart(bot):
    while(True):
        # pick a random action from the list of actions
        action = random.choice(ACTIONS)
        # pose the action
        bot.pose(action)
        # wait a random amount of time between 2 and 3 minutes
        time.sleep(random.randint(120, 180))

if __name__ == "__main__":
    # note that you can either use just the bot token or the player name, lastname , username and password
    bot = MuckletBot.Bot(TOKEN = "<Your Token Here>")
    
    bot.OnMessage = OnMessage
    bot.OnStart = OnStart

    bot.start()
```
## Docs:
First and foremost I would recomend checking out the [original bot](https://github.com/ScientiFox/mucklet-bot-python) as most of the used code has come from there.
