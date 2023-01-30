# PythonMuckletBot
A easy to use bot for the Mucklet engine.


## MuckletBot is a much more simple way to use the [original bot](https://github.com/ScientiFox/mucklet-bot-python) by [ScientiFox](https://github.com/ScientiFox)

There are 2 types of bots, UserBots and Bots
UserBots will require your Username and Password to be passed in as well as the bots name and surname you would like to controll
Bots only require the bots Token

### QuickStart:
```python3
import MuckletBot
import json


# This is the function that will be called when a message is received.
def OnMessage(bot, message):
    print("Recieved")
    if message.loggedMessage:
        print("Logged message: "+message.text)
        if not message.isme:
            try:
                bot.say(f"Hi, {' '.join(message.sender.name)}. You said: {message.text} ({message.type})")
            except Exception as e:
                print(e)
                bot.say("Error: "+str(e))
    # with json pretty print the data:
    print(json.dumps(message.message, indent=4, sort_keys=True))
    print("------------")


# This is the function that will be called when the bot starts.
def OnStart(bot):
    # print the bot's CID to the console for debugging purposes.
    print("Bot "+bot.CID+" has started.")

if __name__ == "__main__":
    # create a new bot instance with your Token
    bot = MuckletBot.Bot(TOKEN = "Your Token Here", VERBOSE = True)
    # set the functions to be called when a message is received and when the bot starts.
    bot.OnMessage = OnMessage
    bot.OnStart = OnStart
    # start the bot.
    bot.start()
```
## Docs:
First and foremost I would recomend checking out the [original bot](https://github.com/ScientiFox/mucklet-bot-python) as most of the used code has come from there.










