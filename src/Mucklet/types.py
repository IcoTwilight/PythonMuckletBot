from Mucklet.ResClient import Request

try:
	from Mucklet.bot import Bot
except ImportError:
	pass


# Properties used by all events
class Character:
	def __init__(self, bot: "Bot", id: str) -> None:
		self.bot: "Bot" = bot
		self.id = id
	
	def __str__(self):
		return f"{self.full_name} ({self.id})"
	
	def __repr__(self):
		return str(self)
	
	def message(self, message: str, pose: bool = False, ooc: bool = False) -> Request:
		return self.bot.message(self, message, pose, ooc)
	
	def whisper(self, message: str, pose: bool = False, ooc: bool = False) -> Request:
		return self.bot.whisper(self, message, pose, ooc)
	
	def address(self, message: str, pose: bool = False, ooc: bool = False) -> Request:
		return self.bot.address(self, message, pose, ooc)
	
	def summon(self):
		return self.bot.summon(self)
	
	def join(self):
		return self.bot.join(self)
	
	def get_avatar(self):
		return str(self.bot.client.cache.get(f"core.char.{self.id}", "avatar"))
	
	def get_awake(self):
		return bool(self.bot.client.cache.get(f"core.char.{self.id}", "awake"))
	
	def get_gender(self):
		return str(self.bot.client.cache.get(f"core.char.{self.id}", "gender"))
	
	def get_idle(self):
		return int(self.bot.client.cache.get(f"core.char.{self.id}", "idle"))
	
	def get_last_awake(self):
		return int(self.bot.client.cache.get(f"core.char.{self.id}", "lastAwake"))
	
	def get_name(self):
		return str(self.bot.client.cache.get(f"core.char.{self.id}", "name"))
	
	def get_species(self):
		return str(self.bot.client.cache.get(f"core.char.{self.id}", "species"))
	
	def get_state(self):
		return str(self.bot.client.cache.get(f"core.char.{self.id}", "state"))
	
	def get_status(self):
		return str(self.bot.client.cache.get(f"core.char.{self.id}", "status"))
	
	def get_surname(self):
		return str(self.bot.client.cache.get(f"core.char.{self.id}", "surname"))
	
	def get_tags(self):
		return list(self.bot.client.cache.get(f"core.char.{self.id}", "tags"))
	
	def get_type(self):
		return str(self.bot.client.cache.get(f"core.char.{self.id}", "type"))
	
	def get_full_name(self):
		return str(self.name + " " + self.surname)
	
	name = property(get_name)
	surname = property(get_surname)
	avatar = property(get_avatar)
	awake = property(get_awake)
	gender = property(get_gender)
	idle = property(get_idle)
	last_awake = property(get_last_awake)
	species = property(get_species)
	state = property(get_state)
	status = property(get_status)
	tags = property(get_tags)
	type = property(get_type)
	
	full_name = property(get_full_name)


class Area:
	def __init__(self, bot: "Bot", id: str):
		self.bot = bot
		self.id = id
	
	def __str__(self):
		return f"{self.name} {self.short_description} ({self.id})"
	
	def __repr__(self):
		return str(self)
	
	def get_about(self):
		return self.bot.client.cache.get(f"core.area.{self.id}.details", "about")
	
	def get_children(self):
		return [Room(self.bot, room) for room in self.bot.client.cache.get(f"core.area.{self.id}.details", "children")]
	
	def get_image(self):
		return self.bot.client.cache.get(f"core.area.{self.id}.details", "image")
	
	def get_map_x(self):
		return self.bot.client.cache.get(f"core.area.{self.id}.details", "mapX")
	
	def get_map_y(self):
		return self.bot.client.cache.get(f"core.area.{self.id}.details", "mapY")
	
	def get_owner(self):
		return Character(self.bot, self.bot.client.cache.get(f"core.area.{self.id}.details", "owner", "id"))
	
	def get_parent(self):
		return Area(self.bot, self.bot.client.cache.get(f"core.area.{self.id}.details", "parent", "id"))
	
	def get_pop(self):
		return self.bot.client.cache.get(f"core.area.{self.id}.details", "pop")
	
	def get_private(self):
		return self.bot.client.cache.get(f"core.area.{self.id}.details", "private")
	
	def get_prv(self):
		return self.bot.client.cache.get(f"core.area.{self.id}.details", "prv")
	
	def get_rules(self):
		return self.bot.client.cache.get(f"core.area.{self.id}.details", "rules")
	
	def get_short_description(self):
		return self.bot.client.cache.get(f"core.area.{self.id}.details", "shortDesc")
	
	def get_name(self):
		return self.bot.client.cache.get(f"core.area.{self.id}.details", "name")
	
	about = property(get_about)
	children = property(get_children)
	image = property(get_image)
	map_x = property(get_map_x)
	map_y = property(get_map_y)
	name = property(get_name)
	owner = property(get_owner)
	parent = property(get_parent)
	pop = property(get_pop)
	private = property(get_private)
	prv = property(get_prv)
	rules = property(get_rules)
	short_description = property(get_short_description)


class Room:
	def __init__(self, bot: "Bot", id: str) -> None:
		self.bot = bot
		self.id = id
	
	def __str__(self):
		return f"{self.name} ({self.id})"
	
	def __repr__(self):
		return str(self)
	
	def get_area(self):
		return Area(self.bot, self.bot.client.cache.get(f"core.room.{self.id}.details", "area", "id"))
	
	def get_autosweep(self):
		return self.bot.client.cache.get(f"core.room.{self.id}.details", "autosweep")
	
	def get_autosweep_delay(self):
		return self.bot.client.cache.get(f"core.room.{self.id}.details", "autosweepDelay")
	
	def get_characters(self):
		return [Character(self.bot, self.bot.client.cache.get(character.get("rid"), "id"))
		        for character in self.bot.client.cache.get(f"core.room.{self.id}.details", "chars")]
	
	def get_description(self) -> str:
		return self.bot.client.cache.get(f"core.room.{self.id}.details", "desc")
	
	def get_exits(self) -> list["Exit"]:
		return [Exit(self.bot, self.bot.client.cache.get(exit.get("rid"), "id"))
		        for exit in self.bot.client.cache.get(f"core.room.{self.id}.details", "exits")]
	
	def get_image(self):
		return self.bot.client.cache.get(f"core.room.{self.id}.details", "image")
	
	def get_is_dark(self):
		return self.bot.client.cache.get(f"core.room.{self.id}.details", "isDark")
	
	def get_is_home(self):
		return self.bot.client.cache.get(f"core.room.{self.id}.details", "isHome")
	
	def get_is_quiet(self):
		return self.bot.client.cache.get(f"core.room.{self.id}.details", "isQuiet")
	
	def get_is_teleport(self):
		return self.bot.client.cache.get(f"core.room.{self.id}.details", "isTeleport")
	
	def get_map_x(self):
		return self.bot.client.cache.get(f"core.room.{self.id}.details", "mapX")
	
	def get_map_y(self):
		return self.bot.client.cache.get(f"core.room.{self.id}.details", "mapY")
	
	def get_name(self):
		return self.bot.client.cache.get(f"core.room.{self.id}.details", "name") or \
			self.bot.client.cache.get(f"core.room.{self.id}", "name")
	
	def get_owner(self):
		return Character(self.bot, self.bot.client.cache.get(f"core.room.{self.id}.details", "owner", "id"))
	
	def get_pop(self):
		return self.bot.client.cache.get(f"core.room.{self.id}.details", "pop")
	
	def get_private(self):
		return self.bot.client.cache.get(f"core.room.{self.id}.details", "private")
	
	area = property(get_area)
	autosweep = property(get_autosweep)
	autosweep_delay = property(get_autosweep)
	characters = property(get_characters)
	description = property(get_description)
	exits = property(get_exits)
	image = property(get_image)
	is_dark = property(get_is_dark)
	is_home = property(get_is_home)
	is_quiet = property(get_is_quiet)
	is_teleport = property(get_is_teleport)
	map_x = property(get_map_x)
	map_y = property(get_map_y)
	name = property(get_name)
	owner = property(get_owner)
	pop = property(get_pop)
	private = property(get_private)


class Exit:
	def __init__(self, bot: "Bot", id: str):
		self.bot = bot
		self.id = id
	
	def __str__(self):
		return f"{self.name} {self.keys} ({self.id})"
	
	def __repr__(self):
		return str(self)
	
	def get_keys(self):
		return self.bot.client.cache.get(f"core.exit.{self.id}.details", "keys", "data") or \
			self.bot.client.cache.get(f"core.exit.{self.id}", "keys", "data")
	
	def get_name(self):
		return self.bot.client.cache.get(f"core.exit.{self.id}.details", "name") or \
			self.bot.client.cache.get(f"core.exit.{self.id}", "name")
	
	def get_arrive_message(self):
		return self.bot.client.cache.get(f"core.exit.{self.id}.details", "arriveMsg")
	
	def get_leave_message(self):
		return self.bot.client.cache.get(f"core.exit.{self.id}.details", "leaveMsg")
	
	def get_created(self):
		return self.bot.client.cache.get(f"core.exit.{self.id}.details", "created")
	
	def get_hidden(self):
		return self.bot.client.cache.get(f"core.exit.{self.id}.details", "hidden")
	
	def get_target_room(self):
		return Room(self.bot, self.bot.client.cache.get(f"core.exit.{self.id}.details", "targetRoom", "id"))
	
	def get_travel_message(self):
		return self.bot.client.cache.get(f"core.exit.{self.id}.details", "travelMsg")
	
	keys = property(get_keys)
	name = property(get_name)
	arrive_message = property(get_arrive_message)
	leave_message = property(get_leave_message)
	created = property(get_created)
	hidden = property(get_hidden)
	target_room = property(get_target_room)
	travel_message = property(get_travel_message)


class EventBase:
	def __init__(self, id: int, type: str, time: float, sig: str):
		self.id = id
		self.type = type
		self.time = time
		self.sig = sig
		self.event = None
	
	def __str__(self):
		return f"{self.type} event {self.id} at {self.time} with signature {self.sig}:\n\tEvent: {self.event}"


# say, pose, wakeup, sleep, leave, arrive, describe, action
class CharacterMessageEvent:
	def __init__(self, character: Character, message: str, puppeteer: Character | None = None):
		self.character = character
		self.message = message
		self.puppeteer = puppeteer
	
	def __str__(self):
		return f"{self.character.name} {self.character.surname} says \"{self.message}\""


# ooc
class CharacterPoseableMessageEvent:
	def __init__(self, character: Character, message: str, pose: bool = False, puppeteer: Character | None = None):
		self.character = character
		self.message = message
		self.pose = pose
		self.puppeteer = puppeteer
	
	def __str__(self):
		return f"{self.character.name} {self.character.surname} says \"{self.message}\""


# whisper, message, warn, mail, address, controlRequest
class TargetedCharacterMessageEvent:
	def __init__(self, character: Character,
	             message: str,
	             target: Character,
	             ooc: bool = False,
	             pose: bool = False,
	             puppeteer: Character | None = None,
	             targets: list[Character] | None = None):
		self.character = character
		self.message = message
		self.target = target
		self.ooc = ooc
		self.pose = pose
		self.puppeteer = puppeteer
		self.targets = targets
		if self.targets is None:
			self.targets = []
		self.targets.append(self.target)
	
	def __str__(self):
		return f"{self.character.name} {self.character.surname} says \"{self.message}\" to " \
		       f"{self.target.name} {self.target.surname}"


# travel
class TargetRoomMessageEvent:
	def __init__(self, character: Character, message: str, target_room: Room, puppeteer: Character | None = None):
		self.character = character
		self.message = message
		self.target = target_room
		self.puppeteer = puppeteer
	
	def __str__(self):
		return f"{self.character.name} {self.character.surname} says \"{self.message}\" to {self.target.name}"


# summon, join, leadRequest, followRequest, follow, stopFollow, stopLead
class TargetedCharacterEvents:
	def __init__(self, character: Character, target: Character, puppeteer: Character | None = None):
		self.character = character
		self.target = target
		self.puppeteer = puppeteer
	
	def __str__(self):
		return f"{self.character.name} {self.character.surname} is targeting {self.target.name} {self.target.surname}"
