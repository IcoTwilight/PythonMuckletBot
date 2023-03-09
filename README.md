# PythonMuckletBot
A easy to use bot for the Mucklet engine.


## MuckletBot is a much more simple way to use the [original bot](https://github.com/ScientiFox/mucklet-bot-python) by [ScientiFox](https://github.com/ScientiFox)

There are 2 types of bots, UserBots and Bots
UserBots will require your Username and Password to be passed in as well as the bots name and surname you would like to controll
Bots only require the bots Token

### QuickStart:
```python3
import MuckletBot
import time
import random

FILLER = [
    "Scratches her ear.",
    "Yawns.",
    "Stretches her arms up in the air - It's been a busy day.",
    "Looks around.",
    "Twitches her ear.",
    "Scrolls through her phone.",
    "Thinks to herself, *what should I do?*",
]

# the function that gets called when a message is recieved
def OnMessage(bot, message):
    # if the message type is either a say, pose, whisper, address or a message
    if message.get("type") in ["say", "pose", "whisper", "address", "message"]:
        # if the recieved message is not from ourself
        if message.get("sender").id != bot.CID:
            # if the message is ping
            if message.get("message").lower().strip() == "ping":
                # send a message pong back to the sender
                message.get("sender").message("pong")
            else:
                # otherwise send the message back to the sender
                bot.message(message.get("sender"), f"You said {message.get('message')}")

# the function that gets called in a seperate thread when the bot is fully booted
def OnOpen(bot):
    # get the CharacterID of Ico Twilight (the code's owner - a.k.a. me)
    id = bot.getCharID("Ico Twilight")
    if id == None:
        # if the character doesn't exist, exit
        bot.Logger("Character not found", title = "RECIEVED ERROR")
    else:
        # send Ico Twilight a message
        bot.message(id, "hiya, I am a bot!")
    while(1):
        # sleep for a random amount of time between 2 minutes and 5 minutes
        time.sleep(random.randint(120, 300))
        # pose a random action from the FILLER
        bot.pose(random.choice(FILLER))

def OnError(bot, error):
    # any errors that occur without an atached promise will be sent here
    bot.Logger(str(error), title = "RECIEVED ERROR WITHOUT PROMISE")

if __name__ == "__main__":
    # create a new bot
    bot = MuckletBot.Bot(TOKEN = "<YOUR TOKEN HERE>", VERBOSE=False)
    # set the onMessage event handler
    bot.onMessage = OnMessage
    # set the onStart event handler
    bot.onOpen = OnOpen
    # set the onError event handler
    bot.onError = OnError
    # start the bot
    bot.run_forever()
    # note if you want to run 1 < bots in the same script, you need to use run() instead of run_forever()
    # then run run_forever() on each bot in a separate thread (see the threading module)
```
## Docs:
First and foremost I would recomend checking out the [original bot](https://github.com/ScientiFox/mucklet-bot-python) as most of the used code has come from there.

`MuckletBot.bot(TOKEN = None, USERNAME = None, PASSWORD = None, BOTFIRSTNAME = None, BOTSURNAME = None, HOST = 'wss://api.test.mucklet.com', ORIGIN = 'https://test.mucklet.com', VERBOSE = False), -> Bot`
Creates a bot object.

`bot.OnMessage`
Overide this function to have any messages be sent to the function specified.

`bot.OnStart`
Overide this function to have the bot run the function specified in a seperate thread when the bot has fully booted.

`bot.start()`
Start and boot the bot.

`bot.sleep()`
Sleep the bot.

`bot.say(message)`
Say a message.

`bot.go(exit)`
go through an exit.

`bot.pose(message)`
Pose a message.

`bot.teleport(node)`
teleport the bot.

`bot.whisper(targetID, message, pose)`
whisper a message to a character.

`bot.address(targetID, message)`
address a message to a character.

`bot.message(targetID, message)`
send a message to a character.

`bot.ping()`
keep the bot awake.

`getID(name)`
This will get the ID from a characters full name. the result will go through the OnMessage function.

`bot.quit()`
sleep the bot and close the connection.
