from .ResClient import ResClient
from .ResClient import Request
from .log import Logger
from .types import Character
from .types import Room
from .types import Exit
from .types import EventBase
from .types import CharacterMessageEvent
from .types import CharacterPoseableMessageEvent
from .types import TargetedCharacterMessageEvent
from .types import TargetRoomMessageEvent
from .types import TargetedCharacterEvents
import time
import sys


class Bot:
	def __init__(self, token: str, client: ResClient):
		self.token = token
		self.client = client
		self.rid = None
		self.id = None
		self.name = None
		self.surname = None
		self.full_name = None
		self.description = None
		self.booted = False
		self.log_info = Logger((75, 75, 200))
		self.log_error = Logger((200, 75, 75), True)
		self.log_success = Logger((75, 200, 75))
		self.on_calls = {"say"           : [],
		                 "pose"          : [],
		                 "wakeup"        : [],
		                 "sleep"         : [],
		                 "leave"         : [],
		                 "arrive"        : [],
		                 "describe"      : [],
		                 "action"        : [],
		                 
		                 "ooc"           : [],
		                 
		                 "whisper"       : [],
		                 "message"       : [],
		                 "warn"          : [],
		                 "mail"          : [],
		                 "address"       : [],
		                 "controlRequest": [],
		                 
		                 "travel"        : [],
		                 
		                 "summon"        : [],
		                 "join"          : [],
		                 "leadRequest"   : [],
		                 "followRequest" : [],
		                 "follow"        : [],
		                 "stopFollow"    : [],
		                 "stopLead"      : [], }
		
		self.match_types = {"say"           : CharacterMessageEvent,
		                    "pose"          : CharacterMessageEvent,
		                    "wakeup"        : CharacterMessageEvent,
		                    "sleep"         : CharacterMessageEvent,
		                    "leave"         : CharacterMessageEvent,
		                    "arrive"        : CharacterMessageEvent,
		                    "describe"      : CharacterMessageEvent,
		                    "action"        : CharacterMessageEvent,
		                    
		                    "ooc"           : CharacterPoseableMessageEvent,
		                    
		                    "whisper"       : TargetedCharacterMessageEvent,
		                    "message"       : TargetedCharacterMessageEvent,
		                    "warn"          : TargetedCharacterMessageEvent,
		                    "mail"          : TargetedCharacterMessageEvent,
		                    "address"       : TargetedCharacterMessageEvent,
		                    "controlRequest": TargetedCharacterMessageEvent,
		                    
		                    "travel"        : TargetRoomMessageEvent,
		                    
		                    "summon"        : TargetedCharacterEvents,
		                    "join"          : TargetedCharacterEvents,
		                    "leadRequest"   : TargetedCharacterEvents,
		                    "followRequest" : TargetedCharacterEvents,
		                    "follow"        : TargetedCharacterEvents,
		                    "stopFollow"    : TargetedCharacterEvents,
		                    "stopLead"      : TargetedCharacterEvents, }
		
		self.waiting_for_response_from = {}  # dict[character: time_sent]
	
	def get_error(self, response: Request, kill: bool = True) -> bool:
		# if there is no error then return False
		if "error" not in response.received_data:
			return False
		# get the error
		error = response.received_data["error"]
		
		# set up the string to log
		string = f"Error: \n"
		
		# if there is a code then add it to the string
		if "code" in error:
			string += f"\t\tCode: {error['code']}\n"
		
		# if there is a message then add it to the string
		if "message" in error:
			string += f"\t\tMessage: {error['message']}\n"
		
		# log the string
		self.log_error(string)
		
		# if the kill flag is set to True then kill the bot
		if kill:
			self.kill()
		
		# if kill flag is set to False then return True
		return True
	
	def get_version(self) -> str:
		self.log_info("Retrieving protocol version")
		version = self.client.version("1.2.1").wait()
		self.get_error(version)
		self.log_success(f"Successfully retrieved protocol version - {version.value().get('result').get('protocol')}")
		return version.value().get('result').get('protocol')
	
	def authenticate(self) -> None:
		self.log_info(f"Authenticating bot - {self.token:.5}...")
		auth = self.client.auth("auth", "authenticateBot",
		                        token = self.token).wait()
		self.get_error(auth, True)
		self.log_success("Successfully authenticated bot")
	
	def get_bot(self) -> None:
		self.log_info(f"Retrieving bot - {self.token:.5}...")
		bot = self.client.call("core", "getBot").wait()
		self.get_error(bot)
		
		self.rid = bot.value().get("result").get("rid")
		data = bot.value().get("result").get("models").get(
				bot.value().get("result").get("models").get(self.rid).get("char").get("rid")
		)
		
		self.name = data.get("name")
		self.surname = data.get("surname")
		self.full_name = f"{self.name} {self.surname}"
		self.description = data.get("desc")
		self.id = data.get("id")
		self.log_success(f"Successfully retrieved bot - {self.full_name}")
	
	def control_bot(self) -> None:
		self.log_info("Controlling bot")
		control = self.client.call("core", "bot", self.id, "controlChar",
		                           charId = self.id).wait()
		self.get_error(control, False)
		self.log_success("Successfully controlled bot")
	
	def subscribe_to_all(self) -> None:
		self.client.subscribe("core", "info").send()
		self.client.subscribe("tag", "info").send()
		self.client.subscribe("mail", "info").send()
		self.client.subscribe("note", "info").send()
		self.client.subscribe("report", "info").send()
		self.client.subscribe("support", "info").send()
		self.client.subscribe("client", "web", "info").send()
		self.client.subscribe("core", "nodes").send()
		self.client.subscribe("tags", "tags").send()
		self.client.subscribe("tags", "groups").send()
		self.client.subscribe("core", "chars", "awake").send()
		
	def on(self, *event: str):
		def decorator(func):
			for e in event:
				if e not in self.on_calls:
					self.log_error(f"Unknown event type - {e}")
					continue
				if func in self.on_calls[e]:
					self.log_error(f"Function already registered - {func}")
					continue
				self.on_calls[e].append(func)
		
		return decorator
	
	def boot(self):
		@self.client.on("message")
		def on_message(message: dict):
			received_data = message
			
			if "id" in received_data:
				return
			
			if "data" not in received_data:
				self.log_error(f"Error - No Data - {received_data}")
				return
			
			if "event" not in received_data:
				self.log_error(f"Error - No Event - {received_data}")
				return
			
			if "type" not in received_data["data"]:
				return
			
			data = received_data["data"]
			
			if "targets" in data:
				self.log_info(f"Recieved multiple targets - {data.get('targets')}")
			
			# now we want to convert the dictionary into its own nested classes
			# create a new EventBase object
			event = EventBase(id = data.get("id"), type = data.get("type"),
			                  time = data.get("time"), sig = data.get("sig"))
			
			# now we want to work out what type of event it is
			if event.type not in self.on_calls:
				self.log_error(f"Unknown event type - {event.type}")
				return
			
			# now we want to create the event object
			event_class = self.match_types[event.type]
			
			if event_class == CharacterMessageEvent:
				event.event = CharacterMessageEvent(
						character = Character(id = data.get("char", {}).get("id"),
						                      bot = self),
						message = data.get("msg"),
						puppeteer = Character(id = data.get("puppeteer", {}).get("id"),
						                      bot = self))
			
			elif event_class == CharacterPoseableMessageEvent:
				event.event = CharacterPoseableMessageEvent(
						character = Character(id = data.get("char", {}).get("id"),
						                      bot = self),
						message = data.get("msg"),
						pose = data.get("pose"),
						puppeteer = Character(id = data.get("puppeteer", {}).get("id"),
						                      bot = self))
			
			elif event_class == TargetedCharacterMessageEvent:
				event.event = TargetedCharacterMessageEvent(
						character = Character(id = data.get("char", {}).get("id"),
						                      bot = self),
						
						message = data.get("msg"),
						target = Character(id = data.get("target", {}).get("id"),
						                   bot = self),
						ooc = data.get("ooc"),
						pose = data.get("pose"),
						puppeteer = Character(id = data.get("puppeteer", {}).get("id"),
						                      bot = self),
						targets = [Character(id = target.get("id"),
						                     bot = self) for target in data.get("targets", [])])
			
			elif event_class == TargetRoomMessageEvent:
				event.event = TargetRoomMessageEvent(
						character = Character(id = data.get("char", {}).get("id"),
						                      bot = self),
						message = data.get("msg"),
						target_room = Room(data.get("targetRoom", {}).get("name"),
						                   data.get("targetRoom", {}).get("id")),
						puppeteer = Character(id = data.get("puppeteer", {}).get("id"),
						                      bot = self))
			
			elif event_class == TargetedCharacterEvents:
				event.event = TargetedCharacterEvents(
						character = Character(id = data.get("char", {}).get("id"),
						                      bot = self),
						target = Character(id = data.get("target", {}).get("id"),
						                   bot = self),
						puppeteer = Character(id = data.get("puppeteer", {}).get("id"),
						                      bot = self))
			
			else:
				self.log_error(f"Error - Unknown Event Class - {event_class}")
				return
			
			# check if the character is the bot
			if event.event.character.id == self.id:
				return
			
			# check if the character.id is in the self.waiting_for_response_from dictionary
			if event.event.character.id in self.waiting_for_response_from:
				# check the type is not a TargetedCharacterEvents
				if event_class != TargetedCharacterEvents:
					self.waiting_for_response_from[event.event.character.id] = event.event.message
					# we want to return here as we don't want to call the on_calls
					return
			
			for func in self.on_calls[event.type]:
				func(event)
		
		@self.client.on("open")
		def on_open():
			self.log_info("Connection opened")
			
			# protocol version
			self.version = self.get_version()
			
			# authenticate
			self.authenticate()
			
			# get the bot
			self.get_bot()
			
			# subscribe to all required resources
			self.subscribe_to_all()
			
			# control the bot
			self.control_bot()
			
			# wake up the bot
			self.wake_up()
			
			self.booted = True
		
		# connect to the server
		if not self.client.running:
			self.client.connect()
		
		while not self.booted:
			time.sleep(0.1)
	
	def wake_up(self) -> None:
		self.log_info("Waking up bot")
		wake_up = self.client.call("core", "char", self.id, "ctrl", "wakeup").wait()
		self.get_error(wake_up, False)
		self.log_success("Successfully woke up bot")
	
	def say(self, message: any) -> Request:
		# {"id":0,"method":"call.core.char.{id}.ctrl.say","params":{"msg":"message"}}
		self.log_info(f"Bot says - \"{str(message)}\"")
		return self.client.call("core", "char", self.id, "ctrl", "say",
		                        msg = str(message)).send()
	
	def pose(self, message: any) -> Request:
		# {"id":0,"method":"call.core.char.{id}.ctrl.pose","params":{"msg":"message"}}
		self.log_info(f"Bot poses - \"{str(message)}\"")
		return self.client.call("core", "char", self.id, "ctrl", "pose",
		                        msg = str(message)).send()
	
	def ooc(self, message: any) -> Request:
		# {"id":0,"method":"call.core.char.{id}.ctrl.ooc","params":{"msg":"message"}}
		self.log_info(f"Bot oocs - \"{str(message)}\"")
		return self.client.call("core", "char", self.id, "ctrl", "ooc",
		                        msg = str(message)).send()
	
	def describe(self, message: any) -> Request:
		# {"id":0,"method":"call.core.char.{id}.ctrl.describe","params":{"msg":"message"}}
		self.log_info(f"Bot describes - \"{str(message)}\"")
		return self.client.call("core", "char", self.id, "ctrl", "describe",
		                        msg = str(message)).send()
	
	def message(self, target: Character, message: any, pose: bool = False, ooc: bool = False) -> Request:
		# {"id":0,"method":"call.core.char.{id}.ctrl.message",
		# "params":{"charId":"{target_id}","msg":"hiya","pose":false, "ooc":false}}
		self.log_info(f"Bot messages - {target.full_name} with \"{str(message)}\"")
		return self.client.call("core", "char", self.id, "ctrl", "message",
		                        charId = target.id,
		                        msg = str(message),
		                        pose = pose,
		                        ooc = ooc).send()
	
	def address(self, target: Character, message: any, pose: bool = False, ooc: bool = False) -> Request:
		# {"id":0,"method":"call.core.char.{id}.ctrl.address",
		# "params":{"charId":"{target_id}","msg":"hiya","pose":false,"ooc":false}}
		self.log_info(f"Bot addresses - {target.full_name} with \"{str(message)}\"")
		return self.client.call("core", "char", self.id, "ctrl", "address",
		                        charId = target.id,
		                        msg = str(message),
		                        pose = pose,
		                        ooc = ooc).send()
	
	def whisper(self, target: Character, message: any, pose: bool = False, ooc: bool = False) -> Request:
		# {"id":0,"method":"call.core.char.{id}.ctrl.whisper",
		# "params":{"charId":"{target_id}","msg":"hiya","pose":false,"ooc":false}}
		self.log_info(f"Bot whispers - {target.full_name} with \"{str(message)}\"")
		return self.client.call("core", "char", self.id, "ctrl", "whisper",
		                        charId = target.id,
		                        msg = str(message),
		                        pose = pose,
		                        ooc = ooc).send()
	
	def mail(self, target: Character, message: any, pose: bool = False, ooc: bool = False) -> None:
		self.log_error("Bot mailing is not implemented!")
		self.log_info("Bots cannot mail for the time being due to requiring player ID's, not character ID's")
		self.log_info("This can be changed by allowing you to add your own player ID to the bot")
		self.log_info("However this is unlikely to be implemented due to the security risks")
		return None
	
	def summon(self, target: Character) -> Request:
		# {"id":0,"method":"call.core.char.{id}.ctrl.summon",
		# "params":{"charId": "{target_id}"}}
		self.log_info(f"Bot summons - {target.full_name}")
		return self.client.call("core", "char", self.id, "ctrl", "summon",
		                        charId = target.id).send()
	
	def join(self, target: Character) -> Request:
		# {"id":0,"method":"call.core.char.{id}.ctrl.join",
		# "params":{"charId":"{target_id}"}}
		self.log_info(f"Bot joins - {target.full_name}")
		return self.client.call("core", "char", self.id, "ctrl", "join",
		                        charId = target.id).send()
	
	def lead(self, target: Character):
		# {"id":0,"method":"call.core.char.{id}.ctrl.lead",
		# "params":{"charId":"{target_id}"}}
		self.log_info(f"Bot leads - {target.full_name}")
		return self.client.call("core", "char", self.id, "ctrl", "lead",
		                        charId = target.id).send()

	def follow(self, target: Character):
		# {"id":0,"method":"call.core.char.{id}.ctrl.follow",
		# "params":{"charId":"{target_id}"}}
		self.log_info(f"Bot follows - {target.full_name}")
		return self.client.call("core", "char", self.id, "ctrl", "follow",
		                        charId = target.id).send()
	
	def stop_lead(self, target: Character):
		# {"id":0,"method":"call.core.char.{id}.ctrl.stopLead",
		# "params":{"charId":"{target_id}"}}
		self.log_info(f"Bot stops leading - {target.full_name}")
		return self.client.call("core", "char", self.id, "ctrl", "stopLead",
		                        charId = target.id).send()

	def stop_follow(self):
		# {"id":0,"method":"call.core.char.{id}.ctrl.stopFollow",
		# "params":{}}
		self.log_info(f"Bot stops following")
		return self.client.call("core", "char", self.id, "ctrl", "stopFollow").send()
	
	def sleep(self) -> Request:
		# {"id":0,"method":"call.core.char.{id}.ctrl.release","params":{}}
		self.log_info("Bot sleeps")
		return self.client.call("core", "char", self.id, "ctrl", "release").send()
	
	def ping(self) -> Request:
		# {"id":0,"method":"call.core.char.{id}.ctrl.ping","params":{}}
		self.log_info("Bot pings")
		return self.client.call("core", "char", self.id, "ctrl", "ping").send()
	
	def wait_for(self, character: Character, timeout: int = 10) -> str:
		# check if we're already waiting for a response from this character
		if character.id in self.waiting_for_response_from:
			self.log_error(f"Error: Bot Already Awaiting Response - {character.full_name}")
			return ""
		# add the character to the dict of characters we're waiting for a response from with value (the time)
		self.waiting_for_response_from[character.id] = time.time()
		# wait for a response from the character
		while type(self.waiting_for_response_from[character.id]) != str:
			# if the timeout is reached, return an empty string
			try:
				if time.time() - self.waiting_for_response_from[character.id] > timeout:
					self.log_info(f"Bot timed out waiting for a response from {character.full_name}")
					del self.waiting_for_response_from[character.id]
					return ""
			except TypeError:
				# another thread has changed the value of the dict entry to a string
				# this means we have a response from the character
				pass
		
		# get the response from the character
		response = self.waiting_for_response_from[character.id]
		# remove the character from the dict of characters we're waiting for a response from
		del self.waiting_for_response_from[character.id]
		# return the response
		return response
	
	def look_up_characters(self, character_name: str) -> list[Character]:
		# {"id":0,"method":"call.core.char.{id}.ctrl.lookUp",
		# "params":{"name":"{character_name}"}}
		names = character_name.split(" ")
		self.log_info(f"Bot looking up characters with the name {names[0]}")
		characters = self.client.call(self.rid, "lookupChars",
		                              name = names[0], extended = True).wait()
		
		self.log_success(characters)
		print("char: ", self.client.cache.get(f"core.char.ccicqnu9gbrk70s5rrdg"))
		
		# {'result': {'payload': {'chars': [{'id': 'ccqvh7m9gbrk70si43e0', 'name': 'Omi', 'surname': 'Lillabi',
		# 'species': 'Mouse', 'gender': 'Male', 'awake': True, 'lastAwake': 1690799543339}]}}, 'id': 8}
		
		if not self.get_error(characters, False):
			characters = [Character(id = character.get("id"),
			                        bot = self)
			              for character in characters.value()["result"]["payload"]["chars"]]
			
			if len(names) > 1:
				# filter out characters that don't have the second name
				self.log_info(f"Bot found {len(characters)} characters with the name {character_name}")
				return [character for character in characters if
				        character.surname.lower() == " ".join(names[1:]).lower()]
			
			else:
				self.log_info(f"Bot found {len(characters)} characters with the name {character_name}")
				return characters
		
		else:
			self.log_error(f"Error - Bot Failed To Look Up Characters - {character_name}")
			return []
	
	def use_exit(self, exit: Exit):
		# {"id":0,"method":"call.core.char.{id}.ctrl.useExit","params":{"exitId":"{exit_id}"}}
		self.log_info(f"Bot uses exit - {exit.name}")
		self.client.call("core", "char", self.id, "ctrl", "useExit", exitId = exit.id).send()
	
	def get_room(self) -> Room:
		return Room(self, self.client.cache.get(f"core.char.{self.id}.owned", "inRoom", "id"))
	
	def kill(self) -> None:
		self.log_info("Killing bot")
		self.sleep()
		self.client.close()
		self.log_success("Successfully killed bot")
		sys.exit()
		