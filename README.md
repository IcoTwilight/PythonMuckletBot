# Mucklet Bot - Docs
This documentation provides a brief overview of the Mucklet Bot library and demonstrates how to use it to create 
and manage a bot for Mucklet's text-based virtual world.

## Instalation

Simply run the following command in your terminal
```shell
pip install mucklet
```

if you get any errors when importing the library, try uninstalling any other websocket libraries you have installed
```shell
pip uninstall websockets
pip uninstall websocket
```

## Getting Started
To create a bot follow these steps to get set up

1 - Import the neccesarry modules
```python
from Mucklet import Bot, ResClient, Logger
import random
```
---
2 - Setup are a logger (not neccesarry)
```python
log_message = Logger((200, 200, 50)) # These are RGB values
```
---
3 - Create the client, this is like the communication between the server and the bot.
```python
client = ResClient("wss://api.test.mucklet.com", "https://test.mucklet.com") # host, origin
```
It is advised to test a bot on the testing realm, failure to do so could result in being banned.

---
4 - Initiate the bot.
```python
bot = Bot("< Put Your Bot Token Here >", client) # Your bot token, the client connection
```
Make sure to replace < Put Your Bot Token Here > with your bot token or the bot will crash

---
5 - add a listener
```python
@bot.on("say") # when the bot hears a say message
def on_say(message):
    log_message(message.event.message) # we will log the message we recieved
    bot.say(message.event.message) # then have the bot say the message that it recieved (it will not respond to itself)
```
---
6 - boot the bot
```python
bot.boot() # start the bot
# any code below will be run after the bot has finished booting
```
---

## Event Handling
The Mucklet Bot library allows you to handle various in-game events by attaching event handlers. Below is a list of all the events that can be listened for:

- `say`: Triggered when a character says something.
- `pose`: Triggered when a character poses.
- `wakeup`: Triggered when a character wakes up.
- `sleep`: Triggered when a character goes to sleep.
- `leave`: Triggered when a character leaves a room.
- `arrive`: Triggered when a character arrives in a room.
- `describe`: Triggered when a character describes something.
- `action`: Triggered when a character performs an action.
- `ooc`: Triggered when a character sends an out-of-character message.
- `whisper`: Triggered when a character whispers to another character.
- `message`: Triggered when a character sends a message to the bot.
- `warn`: Triggered when a character warns the bot.
- `mail`: Triggered when the bot receives mail.
- `address`: Triggered when a character addresses another character.
- `controlRequest`: Triggered when the bot receives a control request.
- `travel`: Triggered when the bot starts traveling to another room.
- `leadRequest`: Triggered when the bot receives a lead request.
- `followRequest`: Triggered when the bot receives a follow request.
- `follow`: Triggered when the bot starts following a character.
- `stopFollow`: Triggered when the bot stops following a character.
- `stopLead`: Triggered when the bot stops leading a character.
- `summon`: Triggered when a character summons another character.
- `join`: Triggered when a character joins another character.

You can attach event handlers to these events using the on method of the Bot class, as shown below:
```python
@bot.on("say")
def on_say(message):
    # Handle the "say" event
    # ...
    pass
```

---

Here are some examples of event handlers that demonstrate how to respond to specific events:


1 - Say example
```python
@bot.on("say")
def on_say(message):
    log_message(f"{message.event.character} says \"{message.event.message}\"")
    bot.say(message.event.message)
```

2 - Summon Example
```python
@bot.on("summon")
def on_summon(message):
    log_message(f"{message.event.character} summons {message.event.target}")
    message.event.character.join()
```

3 - Multiple listeners example
```python
@bot.on("whisper", "address", "message")
def on_target(message):
    log_message(f"{message.event.character} targets {message.event.target} with \"{message.event.message}\"")
    message.event.character.message(message.event.message)
```

## Bot methods:
- ```Bot.__init__(self, token: str, client: ResClient) -> None```
- ```Bot.get_error(self, response: Request, kill: bool = True) -> bool:```
- ```Bot.get_version(self) -> str:```
- ```Bot.authenticate(self) -> None:```
- ```Bot.get_bot(self) -> None:```
- ```Bot.control_bot(self) -> None:```
- ```Bot.subscribe_to_all(self) -> None:```
- ```Bot.on(self, *event: str):```
- ```Bot.boot(self):```
- ```Bot.wake_up(self) -> None:```
- ```Bot.say(self, message: any) -> Request:```
- ```Bot.pose(self, message: any) -> Request:```
- ```Bot.ooc(self, message: any) -> Request:```
- ```Bot.describe(self, message: any) -> Request:```
- ```Bot.message(self, target: Character, message: any, pose: bool = False, ooc: bool = False) -> Request:```
- ```Bot.address(self, target: Character, message: any, pose: bool = False, ooc: bool = False) -> Request:```
- ```Bot.whisper(self, target: Character, message: any, pose: bool = False, ooc: bool = False) -> Request:```
- ```Bot.mail(self, target: Character, message: any, pose: bool = False, ooc: bool = False) -> None:```
- ```Bot.summon(self, target: Character) -> Request:```
- ```Bot.join(self, target: Character) -> Request:```
- ```Bot.lead(self, target: Character):```
- ```Bot.follow(self, target: Character):```
- ```Bot.stop_lead(self, target: Character):```
- ```Bot.stop_follow(self):```
- ```Bot.sleep(self) -> Request:```
- ```Bot.ping(self) -> Request:```
- ```Bot.wait_for(self, character: Character, timeout: int = 10) -> str:```
- ```Bot.look_up_characters(self, character_name: str) -> list[Character]:```
- ```Bot.use_exit(self, exit: Exit):```
- ```Bot.get_room(self) -> Room:```
- ```Bot.kill(self) -> None:```

## ResClient methods:
- ```ResClient.__init__(self, host: str, origin: str):```
- ```ResClient.on_message(self, ws, response):```
- ```ResClient.process_response(self, response: dict) -> None:```
- ```ResClient.display_errors(self, errors: dict) -> None:```
- ```ResClient.cache_dict(self, values: dict) -> None:```
- ```ResClient.version(self, protocol: str) -> Request:```
- ```ResClient.subscribe(self, *rid):```
- ```ResClient.unsubscribe(self, *rid, count = 1):```
- ```ResClient.get(self, *rid):```
- ```ResClient.call(self, *rid: str, **kwargs):```
- ```ResClient.auth(self, *rid, **params):```
- ```ResClient.on(self, event: str):```
- ```ResClient.close(self):```
- ```ResClient.new(self):```

## Request methods:

- ```Request.__init__(self, _connection, *method, notification: bool = False, **params):```
- ```Request.send(self) -> "Request":```
- ```Request.resend(self) -> None:```
- ```Request.receive(self, data: dict) -> None:```
- ```Request.wait(self, time_out_period: int = None) -> "Request":```
- ```Request.kill(self) -> None:```
- ```Request.value(self) -> dict:```

## Cache methods:

- ```Cache.__init__(self, client: "ResClient", data: any = None):```
- ```Cache.get(self, *rids: str, default: any = None) -> any:```
- ```Cache.set(self, rid: str, value: any) -> None:```
- ```Cache.change(self, rid: str, values: dict) -> None:```
- ```Cache.add(self, rid: str, index: int, value: dict) -> None:```
- ```Cache.remove(self, rid: str, index: int) -> None:```
- ```Cache.__getitem__(self, item: any) -> any:```
- ```Cache.__setitem__(self, key: str, value: any) -> None:```
- ```Cache.__delitem__(self, key: str) -> None:```
- ```Cache.__str__(self) -> str:```
- ```Cache.__repr__(self) -> str:```
- ```Cache.__contains__(self, item: str) -> bool:```

## Logger methods

- ```Logger.__init__(self, format_color: tuple[int, int, int] = (255, 50, 50), bold: bool = True):```
- ```Logger.__call__(self, _message: any, _raise: bool = False) -> None:```
- ```Logger.reset(cls) -> None:``` (classmethod)
- ```Logger.hide(cls) -> None:``` (classmethod)
- ```Logger.show(cls) -> None:``` (classmethod)
- ```Logger.toggle(cls) -> None:``` (classmethod)
- ```Logger.log_if_not_shown(cls, _message: str, color = (255, 255, 255)) -> None:``` (classmethod)
- ```Logger.iteration = 0``` (class attribute)
- ```Logger.shown = True```  (class attribute)

## Character methods:
- ```Character.__init__(self, bot: "Bot", id: str) -> None:```
- ```Character.__str__(self):```
- ```Character.__repr__(self):```
- ```Character.message(self, message: str, pose: bool = False, ooc: bool = False) -> Request:```
- ```Character.whisper(self, message: str, pose: bool = False, ooc: bool = False) -> Request:```
- ```Character.address(self, message: str, pose: bool = False, ooc: bool = False) -> Request:```
- ```Character.summon(self):```
- ```Character.join(self):```
- ```Character.get_avatar(self):``` (accessed by property)
- ```Character.get_awake(self):``` (accessed by property)
- ```Character.get_gender(self):``` (accessed by property)
- ```Character.get_idle(self):``` (accessed by property)
- ```Character.get_last_awake(self):``` (accessed by property)
- ```Character.get_name(self):``` (accessed by property)
- ```Character.get_species(self):``` (accessed by property)
- ```Character.get_state(self):``` (accessed by property)
- ```Character.get_status(self):``` (accessed by property)
- ```Character.get_surname(self):``` (accessed by property)
- ```Character.get_tags(self):``` (accessed by property)
- ```Character.get_type(self):``` (accessed by property)
- ```Character.get_full_name(self):``` (accessed by property)
- ```Character.get_local_storage(self)```

- ```name = property(get_name)``` (property)
- ```surname = property(get_surname)``` (property)
- ```avatar = property(get_avatar)``` (property)
- ```awake = property(get_awake)``` (property)
- ```gender = property(get_gender)``` (property)
- ```idle = property(get_idle)``` (property)
- ```last_awake = property(get_last_awake)``` (property)
- ```species = property(get_species)``` (property)
- ```state = property(get_state)``` (property)
- ```status = property(get_status)``` (property)
- ```tags = property(get_tags)``` (property)
- ```type = property(get_type)``` (property)
- ```local_storage = property(get_local_storage)``` (property)
	
- ```full_name = property(get_full_name)``` (property)

## Area methods

- ```Area.__init__(self, bot: "Bot", id: str):```
- ```Area.__str__(self):```
- ```Area.__repr__(self):```
- ```Area.get_about(self):``` (accessed by property)
- ```Area.get_children(self):``` (accessed by property)
- ```Area.get_image(self):``` (accessed by property)
- ```Area.get_map_x(self):``` (accessed by property)
- ```Area.get_map_y(self):``` (accessed by property)
- ```Area.get_owner(self):``` (accessed by property)
- ```Area.get_parent(self):``` (accessed by property)
- ```Area.get_pop(self):``` (accessed by property)
- ```Area.get_private(self):``` (accessed by property)
- ```Area.get_prv(self):``` (accessed by property)
- ```Area.get_rules(self):``` (accessed by property)
- ```Area.get_short_description(self):``` (accessed by property)
- ```Area.get_name(self):``` (accessed by property)
- ```Area.about = property(get_about)``` (property)
- ```Area.children = property(get_children)``` (property)
- ```Area.image = property(get_image)``` (property)
- ```Area.map_x = property(get_map_x)``` (property)
- ```Area.map_y = property(get_map_y)``` (property)
- ```Area.name = property(get_name)``` (property)
- ```Area.owner = property(get_owner)``` (property)
- ```Area.parent = property(get_parent)``` (property)
- ```Area.pop = property(get_pop)``` (property)
- ```Area.private = property(get_private)``` (property)
- ```Area.prv = property(get_prv)``` (property)
- ```Area.rules = property(get_rules)``` (property)
- ```Area.short_description = property(get_short_description)``` (property)

## Room methods:
- ```Area.__init__(self, bot: "Bot", id: str) -> None:```
- ```Area.__str__(self):```
- ```Area.__repr__(self):```
- ```Area.get_area(self):``` (accessed by property)
- ```Area.get_autosweep(self):``` (accessed by property)
- ```Area.get_autosweep_delay(self):``` (accessed by property)
- ```Area.get_characters(self):``` (accessed by property)
- ```Area.get_description(self) -> str:``` (accessed by property)
- ```Area.get_exits(self) -> list["Exit"]:``` (accessed by property)
- ```Area.get_image(self):``` (accessed by property)
- ```Area.get_is_dark(self):``` (accessed by property)
- ```Area.get_is_home(self):``` (accessed by property)
- ```Area.get_is_quiet(self):``` (accessed by property)
- ```Area.get_is_teleport(self):``` (accessed by property)
- ```Area.get_map_x(self):``` (accessed by property)
- ```Area.get_map_y(self):``` (accessed by property)
- ```Area.get_name(self):``` (accessed by property)
- ```Area.get_owner(self):``` (accessed by property)
- ```Area.get_pop(self):``` (accessed by property)
- ```Area.get_private(self):``` (accessed by property)

- ```Area.area = property(get_area)``` (property)
- ```Area.autosweep = property(get_autosweep)``` (property)
- ```Area.autosweep_delay = property(get_autosweep)``` (property)
- ```Area.characters = property(get_characters)``` (property)
- ```Area.description = property(get_description)``` (property)
- ```Area.exits = property(get_exits)``` (property)
- ```Area.image = property(get_image)``` (property)
- ```Area.is_dark = property(get_is_dark)``` (property)
- ```Area.is_home = property(get_is_home)``` (property)
- ```Area.is_quiet = property(get_is_quiet)``` (property)
- ```Area.is_teleport = property(get_is_teleport)``` (property)
- ```Area.map_x = property(get_map_x)``` (property)
- ```Area.map_y = property(get_map_y)``` (property)
- ```Area.name = property(get_name)``` (property)
- ```Area.owner = property(get_owner)``` (property)
- ```Area.pop = property(get_pop)``` (property)
- ```Area.private = property(get_private)``` (property)

## Exit methods:

- ```Exit.__init__(self, bot: "Bot", id: str):```
- ```Exit.__str__(self):```
- ```Exit.__repr__(self):```
- ```Exit.get_keys(self):```
- ```Exit.get_name(self):```
- ```Exit.get_arrive_message(self):```
- ```Exit.get_leave_message(self):```
- ```Exit.get_created(self):```
- ```Exit.get_hidden(self):```
- ```Exit.get_target_room(self):```
- ```Exit.get_travel_message(self):```

- ```Exit.s = property(get_keys)```
- ```Exit.name = property(get_name)```
- ```Exit.arrive_message = property(get_arrive_message)```
- ```Exit.leave_message = property(get_leave_message)```
- ```Exit.created = property(get_created)```
- ```Exit.hidden = property(get_hidden)```
- ```Exit.target_room = property(get_target_room)```
- ```Exit.travel_message = property(get_travel_message)```

## EventBase methods:

- ```EventBase.__init__(self, id: int, type: str, time: float, sig: str):```
- ```EventBase.__str__(self):```

## CharacterMessageEvent methods:

- ```CharacterMessageEvent.__init__(self, character: Character, message: str, puppeteer: Character | None = None):```
- ```CharacterMessageEvent.__str__(self):```

## CharacterPoseableMessageEvent methods:
- ```CharacterPoseableMessageEvent__init__(self, character: Character, message: str, pose: bool = False, puppeteer: Character | None = None):```
- ```CharacterPoseableMessageEvent__str__(self):```

## TargetedCharacterMessageEvent methods:
- ```TargetedCharacterMessageEvent.__init__(self, character: Character, message: str, target: Character, ooc: bool = False, pose: bool = False, puppeteer: Character | None = None, targets: list[Character] | None = None):```
- ```TargetedCharacterMessageEvent.__str__(self):```

## TargetRoomMessageEvent methods:
- ```TargetRoomMessageEvent.__init__(self, character: Character, message: str, target_room: Room, puppeteer: Character | None = None):```
- ```TargetRoomMessageEvent.__str__(self):```

## TargetedCharacterEvents methods:
- ```__init__(self, character: Character, target: Character, puppeteer: Character | None = None):```
- ```__str__(self):```
