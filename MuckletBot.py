# MuckletBotCombined.py
# a combined bot for the MuckletBot
import websocket
import json
import threading
import time
import hashlib
import hmac
import codecs

LOGIN = 1
GET_PLAYER = 2
GET_CHARS = 3
CHAR_CTRL = 4
CTRL_BOT = 5
WAKEUP = 6
GO = 7
SAY = 8
SLEEP = 9
SUBSCRIBE = 10
UNSUBSCRIBE = 11
POSE = 12
TELEPORT = 13
WHISPER = 14
ADDRESS = 15
MESSAGE = 16
PING = 17

class Logger:
    def __init__(self, type = "Log", wraping = "=", indent = 4, indentChar = " "):
        self.type = type
        self.wraping = wraping
        self.indent = indent
        self.indentChar = indentChar
        self.i = 1
    def log(self, *messages):
        print(f"{self.wraping*self.indent} {self.type} {self.wraping*self.indent}")
        for message in messages:
            print(f"{self.i}: {self.indentChar*self.indent}{message}")
            self.i += 1
        print(f"{self.wraping*(self.indent*2+len(self.type)+2)}")

class Character:
    def __init__(self, bot, playerFirstName = None, playerSurName = None, playerID = None):
        self.bot = bot
        self.firstName = playerFirstName
        self.surName = playerSurName
        self.surname = self.surName
        self.secondName = self.surName
        self.name = (self.firstName, self.surName)
        self.id = playerID

class Message:
    def __init__(self, bot, message):
        self.bot = bot
        self.raw = message
        if self.raw.get("error"):
            self.errorCode = self.raw.get("error").get("code")
            self.errorMessage = self.raw.get("error").get("message")
            return
        else:
            self.errorCode = None
            self.errorMessage = None
        if self.result():
            self.eventPlace = None
            self.eventCID = None
            self.eventType = None
        else:
            split = self.raw.get("event").split(".") # split the event into its parts.
            self.eventPlace = split[1]
            self.eventCID = split[2]
            self.eventType = ".".join(split[3:])
    def type(self):
        if self.raw.get("data"):
            return self.raw.get("data").get("type")
        return None
    def sender(self):
        if self.raw.get("data"):
            char = self.raw.get("data").get("char")
            if char:
                # cunstruct a new character object.
                return Character(self.bot, char.get("name"), char.get("surname"), char.get("id"))
        return None
    def message(self):
        if self.raw.get("data"):
            return self.raw.get("data").get("msg")
        return None
    def time(self):
        if self.raw.get("data"):
            return self.raw.get("data").get("time")
        return None
    def signature(self):
        if self.raw.get("data"):
            return self.raw.get("data").get("sig")
        return None
    def id(self):
        if self.raw.get("data"):
            return self.raw.get("data").get("id")
        return None
    def target(self):
        if self.raw.get("data"):
            target = self.raw.get("data").get("target")
            if target:
                # cunstruct a new character object.
                return Character(self.bot, target.get("name"), target.get("surname"), target.get("id"))
        return None
    def event(self):
        return self.raw.get("event")
    def fromSelf(self):
        if self.sender():
            return self.sender().id == self.bot.CID
        else:
            return None
    def toSelf(self):
        return self.eventCID == self.bot.CID
    def result(self):
        return self.raw.get("result")
    
    # fromself returns true if the message is from the bot and not another awake character.
    # toSelf returns true if the message is for the bot and not another awake character.

    def __str__(self):
        string = f"Message Object:\n"
        string += f"\t{self.raw=}\n"
        string += f"\t{self.eventPlace=}\n"
        string += f"\t{self.eventCID=}\n"
        string += f"\t{self.eventType=}\n"
        string += f"\t{self.type()=}\n"
        string += f"\t{self.sender()=}\n"
        string += f"\t{self.message()=}\n"
        string += f"\t{self.time()=}\n"
        string += f"\t{self.signature()=}\n"
        string += f"\t{self.id()=}\n"
        string += f"\t{self.target()=}\n"
        string += f"\t{self.event()=}\n"
        string += f"\t{self.fromSelf()=}\n"
        string += f"\t{self.toSelf()=}\n"
        string += f"\t{self.result()=}\n"
        return string
    

class Bot:
    def __init__(self, TOKEN = None, USERNAME = None, PASSWORD = None, BOTFIRSTNAME = None, BOTSURNAME = None, HOST = 'wss://api.test.mucklet.com', ORIGIN = 'https://test.mucklet.com', VERBOSE = False):
        # create the logging classes.
        self.BootingLog = Logger("Booting Info")
        self.MessageLogger = Logger("Recieved Message")
        self.SendingLogger = Logger("Sending Message")
        self.ErrorLogger = Logger("Error")
        self.characterLogger = Logger("Character Info")
        # work out if the user is using a token or a username and password.
        if TOKEN:
            self.TOKEN = TOKEN
            self.BOTTYPE = "bot"
        elif USERNAME and PASSWORD and BOTFIRSTNAME and BOTSURNAME:
            self.USERNAME = USERNAME
            self.PASSWORD = PASSWORD
            self.BOTFIRSTNAME = BOTFIRSTNAME
            self.BOTSURNAME = BOTSURNAME
            self.BOTTYPE = "player"
        else:
            raise Exception("You must provide either a token or a username, password, first name and surname of the bot.")
        # set the host and origin.
        self.HOST = HOST
        self.ORIGIN = ORIGIN
        # set the verbose flag.
        self.VERBOSE = VERBOSE
        # set the functions to be called when a message is received and when the bot starts.
        self.OnMessage = None
        self.OnStart = None
        # set the bot's CID.
        self.CID = None
        # set the bot's RID.
        self.RID = None
        # set the ws.
        self.ws = None
        # set the boot index.
        self.bootIndex = 0
        # create the players hash if the player type is a player
        if self.BOTTYPE == "player":
            self.BootingLog.log("Creating the players hash.")
            self.pepper = "TheStoryStartsHere"
            m = hashlib.sha256()
            m.update(bytes(self.PASSWORD,'UTF-8'))
            hx = m.hexdigest()
            self.PASS = codecs.encode(codecs.decode(hx, 'hex'), 'base64').decode()[:-1]
            hx = hmac.new(bytes(self.pepper,'UTF-8'),msg=bytes(self.PASSWORD,'UTF-8'), digestmod = hashlib.sha256).hexdigest()
            self.HASH = codecs.encode(codecs.decode(hx, 'hex'), 'base64').decode()[:-1]
    def send(self, ws,method,ind=0,params = None):
        #Helper function to wrap WS function
        request = {"id":ind,"method":method,"params":params}
        msg = json.dumps(request)
        ws.send(msg)
        if self.VERBOSE:
            self.SendingLogger.log(f"{msg}")

    def on_message(self, ws, message):
        #Message handler- basically everything taps here
        msg = json.loads(message) #make it a dictionary

        #Be loud?
        if self.VERBOSE:
            self.MessageLogger.log(f"{msg}")

        #Error message handler- currently just to pass boot if already controlled or awake
        if 'error' in msg and self.bootIndex < 6:
            if self.bootIndex == 4 and msg['id'] == CTRL_BOT:
                self.bootIndex = 5
            if self.bootIndex == 5 and msg['id'] == WAKEUP:
                self.bootIndex = 6
        elif 'error' in msg:
            #log errors outside boot cycle
            self.ErrorLogger.log(f"{msg}")

        #For reply responses
        if 'result' in msg and self.bootIndex < 7:

            #Boot Cycle syncing
            #The login and setup are only allowed to proceed once each
            #  requested message arrives, and is processed
            if self.bootIndex == 1 and msg["id"] == LOGIN:
                self.bootIndex = 2
            if self.bootIndex == 2 and msg["id"] == GET_PLAYER:
                self.RID = msg['result']['rid']
                self.CID = self.RID.split('.')[-1]
                self.bootIndex = 3
            if self.bootIndex == 3 and msg['id'] == GET_CHARS:
                if self.BOTTYPE == "player":
                    characters = []
                    #Grab the char data to search to ID the bot
                    chars = msg["result"]["collections"][self.RID+".chars"]
                    chars = [a['rid'] for a in chars] #Get the actual refs
                    for ch in chars:
                        #Loop over the chars
                        char_data = msg["result"]["models"][ch]
                        characters.append(char_data["name"] + " " + char_data["surname"] + " : " + char_data['id'])
                        if char_data["name"] == self.BOTFIRSTNAME and char_data["surname"] == self.BOTSURNAME:
                            #If find the bot's name, get its ID and make the char object
                            self.CID = char_data["id"]
                    self.characterLogger.log(*characters)
                else:
                    pass
                self.bootIndex = 4
            if self.bootIndex == 4 and msg['id'] == CTRL_BOT:
                self.bootIndex = 5
            if self.bootIndex == 5 and msg['id'] == WAKEUP:
                self.bootIndex = 6
            if self.bootIndex == 6 and msg['id'] == GET_CHARS:

                #Grab the initial player data models and collections after 1st subscription
                self.CharacterModels      = msg["result"]["models"]
                self.CharacterCollections = msg["result"]["collections"]

                #Mark done with boot cycle
                self.bootIndex = 7
        else:
            #If not in boot cycle, pass message to user's OnMessage function if it exists
            if self.OnMessage != None:
                self.OnMessage(self, Message(self, msg))
            else:
                if self.VERBOSE:
                    self.ErrorLogger.log("No OnMessage function defined.")
        

    def on_error(self, ws, error):
        #Helper function to wrap WS function
        self.ErrorLogger.log(f"{error}")

    def on_close(self, ws, close_status_code = None, close_msg = None):
        #Helper function to wrap WS function
        if self.VERBOSE:
            self.BootingLog.log('connection closed')

    def on_open(self, ws):
        #Helper function to wrap WS function
        if self.VERBOSE:
            self.BootingLog.log('connection opened')
        self.bootIndex = 1
        self.ws = ws
        # thread the boot cycle
        bootCycle = threading.Thread(target=self.boot)
        bootCycle.start()
    
    def start(self):
        #Build the websocket w/ bot methods as callbacks
        #websocket.enableTrace(True)
        ws = websocket.WebSocketApp(self.HOST
                                    ,on_message = self.on_message
                                    ,on_error   = self.on_error
                                    ,on_close   = self.on_close
                                    ,on_open    = self.on_open)

        #Fire up the websocket
        ws.run_forever(origin=self.ORIGIN)
    
    def boot(self):

        #Boot sequence started in separate thread, waits until on_open is called in WS
        #In thread to have messages, so it's run in order to build the char objects cleanly
        self.BootingLog.log("Authenticating")
        #Authenticate and get the player info
        if self.BOTTYPE == "bot":
            params = {"token":self.TOKEN}
            self.send(self.ws,'auth.auth.authenticateBot',params=params,ind=LOGIN)
        else:
            params = {  "name":self.USERNAME,
                        "hash":self.HASH}
            self.send(self.ws,'auth.auth.login',params=params,ind=LOGIN)
        while (self.bootIndex == 1):
            time.sleep(0.1)

        self.BootingLog.log("Getting Player RID")
        #Get Player rid
        if self.BOTTYPE == "bot":
            self.send(self.ws,'call.core.getBot',ind=GET_PLAYER)
        else:
            self.send(self.ws,'call.core.getPlayer',ind=GET_PLAYER)
        while(self.bootIndex == 2):
            time.sleep(0.1)

        self.BootingLog.log("Getting Character Data")
        #Get character data
        self.send(self.ws,"get."+self.RID,ind=GET_CHARS)
        while(self.bootIndex == 3):
            time.sleep(0.1)

        self.BootingLog.log("Controlling Bot")
        #Take control of the bot character
        method = "call."+self.RID+".controlChar"
        self.send(self.ws,method,params={'charId':self.CID},ind=CTRL_BOT)
        while(self.bootIndex == 4):
            time.sleep(0.1)

        self.BootingLog.log("Waking Bot")
        #Wake the bot up
        method = "call.core.char."+self.CID+".ctrl.wakeup"
        self.send(self.ws,method,ind=WAKEUP)
        while(self.bootIndex == 5):
            time.sleep(0.1)

        self.BootingLog.log("Subscribing to all incoming data")
        #Get looking character data
        self.send(self.ws,"subscribe."+self.RID,ind=GET_CHARS)
        while(self.bootIndex == 6):
            time.sleep(0.1)

        #Done booting
        self.BootingLog.log("Done booting")

        #Call user's OnStart function if it exists in a new thread
        if self.OnStart != None:
            onStartThread = threading.Thread(target=self.OnStart, args=(self,))
            onStartThread.start()
        else:
            if self.VERBOSE:
                self.ErrorLogger.log("No OnStart function defined.")

    def sleep(self):
        method = "call.core.char."+self.CID+".ctrl.sleep"
        self.send(self.ws,method,params={},ind=SLEEP)

    def say(self, msg):
        method = "call.core.char."+self.CID+".ctrl.say"
        self.send(self.ws,method,params={'msg':msg},ind=SAY)

    def go(self, ext):
        method = "call.core.char."+self.CID+".ctrl.useExit"
        self.send(self.ws,method,params={'exitId':ext.split(".")[-1]},ind=GO)

    def pose(self, msg):
        method = "call.core.char."+self.CID+".ctrl.pose"
        self.send(self.ws,method,params={'msg':msg},ind=POSE)

    def teleport(self,nodeId):
        method = "call.core.char."+self.CID+".ctrl.teleport"
        self.send(self.ws,method,params={'nodeId':nodeId},ind=TELEPORT)

    def whisper(self, targetId, msg, pose='whispers'):
        method = "call.core.char."+self.CID+".ctrl.whisper"
        self.send(self.ws,method,params={'msg':msg,'charId':targetId,'pose':pose},ind=WHISPER)

    def address(self, targetId, msg):
        method = "call.core.char."+self.CID+".ctrl.address"
        self.send(self.ws,method,params={'msg':msg,'charId':targetId},ind=ADDRESS)

    def message(self, targetId, msg):
        method = "call.core.char."+self.CID+".ctrl.message"
        self.send(self.ws,method,params={'msg':msg,'charId':targetId},ind=MESSAGE)

    def ping(self):
        method = "call.core.char."+self.CID+".ctrl.ping"
        self.send(self.ws,method,params={},ind=PING)
    
    def getID(self, name):
        method = "call."+self.RID+".getChar"
        self.send(self.ws, method, params={"charName": name})
    
    def quit(self):
        self.sleep()
        self.ws.close()
