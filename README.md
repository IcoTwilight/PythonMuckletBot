# PythonMuckletBot
A easy to use bot for the Mucklet engine.


## MuckletBot is a much more simple way to use the [original bot](https://github.com/ScientiFox/mucklet-bot-python) by [ScientiFox](https://github.com/ScientiFox)

There are 2 types of bots, UserBots and Bots
UserBots will require your Username and Password to be passed in as well as the bots name and surname you would like to controll
Bots only require the bots Token

### A Bot that will reply to any message (say, pose, message... e.t.c.) that is "ping":
```python3
import MuckletBot

# This is the function that will be called when a message is received.
def OnMessage(bot, message):
    # print the message(dict) to the console for debugging purposes.
    print(message)
    # get the data from the message.
    data = message.get("data")
    # check if the data is not empty.
    if data:
        # check if the message is not from the bot itself.
        if data.get("char").get("id") != bot.CID:
            # check if the message is ping.
            if data.get("msg") == "ping":
                # say pong.
                bot.say("pong")

# This is the function that will be called when the bot starts.
def OnStart(bot):
    # print the bot's CID to the console for debugging purposes.
    print("Bot "+bot.CID+" has started.")

if __name__ == "__main__":
    # create a new bot instance with your Token
    bot = MuckletBot.Bot(TOKEN="YOUR TOKEN HERE")
    # set the functions to be called when a message is received and when the bot starts.
    bot.OnMessage = OnMessage
    bot.OnStart = OnStart
    # start the bot.
    bot.start()
```
