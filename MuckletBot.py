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

class LoginError(Exception):
    def __init__(self, message):
        self.message = message

class Logger:
    def __init__(self, logfile = None, indent = 4, wrapping = "="):
        self.logfile = logfile
        self.indent = indent
        self.wrapping = wrapping
        self.i = 0
    def __call__(self, *messages, title = ""): self.log(*messages, title = title)
    def log(self, *messages, title = ""):
        string = self.wrapping*5 + " " + title + " " + self.wrapping*5 + "\n"
        for message in messages:
            self.i += 1
            string += str(self.i) + ":" + " "*self.indent + str(message) + "\n"
        string += self.wrapping*6+ self.wrapping*len(title) + self.wrapping*6 + "\n"

        if self.logfile is not None:
            with open(self.logfile, "a") as f:
                f.write(string)
        print(string)

class Character:
    def __init__(self, bot, name = None, id = None):
        self.bot = bot
        self.name = name
        self.id = id
    def message(self, message):
        self.bot.message(self, message)
    def whisper(self, message):
        self.bot.whisper(self, message)
    def address(self, message):
        self.bot.address(self, message)
    def getID(self):
        if self.id is None:
            self.id = self.bot.getCharID(self.name)
        return self.id

class Bot:
    def __init__(self, TOKEN:str = None, USERNAME:str = None, PASSWORD:str = None, BOTFIRSTNAME:str = None, BOTLASTNAME:str = None, HOST:str = 'wss://api.test.mucklet.com', ORIGIN:str = 'https://test.mucklet.com', VERBOSE:bool = False):
        self.Logger = Logger()
        self.TOKEN = TOKEN
        if self.TOKEN is not None:
            pass
        elif USERNAME is not None and PASSWORD is not None and BOTFIRSTNAME is not None and BOTLASTNAME is not None:
            self.BOTFIRSTNAME = BOTFIRSTNAME
            self.BOTLASTNAME = BOTLASTNAME
            self.USERNAME = USERNAME
            self.pepper = "TheStoryStartsHere"
            m = hashlib.sha256()
            m.update(bytes(PASSWORD,'UTF-8'))
            hx = m.hexdigest()
            self.PASS = codecs.encode(codecs.decode(hx, 'hex'), 'base64').decode()[:-1]
            hx = hmac.new(bytes(self.pepper,'UTF-8'),msg=bytes(PASSWORD,'UTF-8'), digestmod = hashlib.sha256).hexdigest()
            self.HASH = codecs.encode(codecs.decode(hx, 'hex'), 'base64').decode()[:-1]
            self.Logger.log(f"Generated HASH: {self.HASH} and PASS: {self.PASS}", title = "Boot")
        else:
            raise LoginError("Invalid amount of login details provided. Must provide either a [token] or a [username, password, botfirstname, botlastname]")
        self.HOST = HOST
        self.ORIGIN = ORIGIN
        self.VERBOSE = VERBOSE

        self.onMessage = None
        self.onOpen = None
        self.onClose = None
        self.onError = None

        self.CID = None
        self.RID = None

        self.awaitingPromise = False
        self.recievedPromise = None
        self.promiseSetTime = None
        self.promiseTimeout = 3

        self.ws = None
    
    def request(self, ws, method,ind=0,params = None):
        # if the awaiting promise timeout has been reached, reset the promise
        while(self.awaitingPromise == True):
            if self.awaitingPromise and time.time() - self.promiseSetTime > self.promiseTimeout:
                self.awaitingPromise = False
                self.recievedPromise = None
                self.promiseSetTime = None
        # if the promise is not awaiting, send the request
        if not self.awaitingPromise:
            self.awaitingPromise = True
            self.recievedPromise = None
            self.promiseSetTime = time.time()
            self.send(ws, method,ind,params,True)
            while self.awaitingPromise:
                continue
            recievedPromise = self.recievedPromise
            self.recievedPromise = None
            self.promiseSetTime = None
            self.awaitingPromise = False
            return recievedPromise
    
    def send(self, ws, method,ind=0,params = None, request = False):
        request = {"id":ind,"method":method,"params":params}
        msg = json.dumps(request)
        ws.send(msg)
        if self.VERBOSE:
            self.Logger.log(f"{msg}", title = "Requested" if request else "Sent")

    def on_message(self, ws, message):
        message = json.loads(message)
        raw = message
        if self.VERBOSE:
            self.Logger.log(message, title = "Recieved")
        if "result" in message or "error" in message:
            if self.awaitingPromise:
                self.recievedPromise = message
                self.awaitingPromise = False
                self.promiseSetTime = None
            else:
                if self.VERBOSE:
                    self.Logger.log(message, title = "Result Recieved, But With No Promise")
                if self.onError is not None:
                    self.onError(self, message)
        else:
            type = "Unknown"
            data = {}
            place = "Unknown"
            if "event" in message:
                event = message.get("event").split(".")
                place = event[1]
                type = event[-2:]
            if "data" in message:
                data = message.get("data")
            if "type" in data:
                type = data.get("type")

            if type == "say":
                message = {
                    "type": "say",
                    "message": data.get("msg"),
                    "sender": Character(self, data.get("char").get("name") + " " + data.get("char").get("surname"), data.get("char").get("id")),
                    "place": place,
                    "time": data.get("time") # unix timestamp (thats seconds since 1970)
                }
            elif type == "pose":
                message = {
                    "type": "pose",
                    "message": data.get("msg"),
                    "sender": Character(self, data.get("char").get("name") + " " + data.get("char").get("surname"), data.get("char").get("id")),
                    "place": place,
                    "time": data.get("time") # unix timestamp (thats seconds since 1970)
                }
            elif type == "describe":
                message = {
                    "type": "describe",
                    "message": data.get("msg"),
                    "sender": Character(self, data.get("char").get("name") + " " + data.get("char").get("surname"), data.get("char").get("id")),
                    "place": place,
                    "time": data.get("time") # unix timestamp (thats seconds since 1970)
                }
            elif type == "whisper":
                message = {
                    "type": "whisper",
                    "message": data.get("msg"),
                    "sender": Character(self, data.get("char").get("name") + " " + data.get("char").get("surname"), data.get("char").get("id")),
                    "reciever": Character(self, data.get("target").get("name") + " " + data.get("target").get("surname"), data.get("target").get("id")),
                    "place": place,
                    "time": data.get("time") # unix timestamp (thats seconds since 1970)
                }
            elif type == "message":
                message = {
                    "type": "message",
                    "message": data.get("msg"),
                    "sender": Character(self, data.get("char").get("name") + " " + data.get("char").get("surname"), data.get("char").get("id")),
                    "reciever": Character(self, data.get("target").get("name") + " " + data.get("target").get("surname"), data.get("target").get("id")),
                    "place": place,
                    "time": data.get("time") # unix timestamp (thats seconds since 1970)
                }
            elif type == "address":
                message = {
                    "type": "address",
                    "message": data.get("msg"),
                    "sender": Character(self, data.get("char").get("name") + " " + data.get("char").get("surname"), data.get("char").get("id")),
                    "reciever": Character(self, data.get("target").get("name") + " " + data.get("target").get("surname"), data.get("target").get("id")),
                    "place": place,
                    "time": data.get("time") # unix timestamp (thats seconds since 1970)
                }
            else:
                message = {
                    "type": "Unknown",
                    "message": raw,
                }
            
            if self.onMessage is not None:
                if raw.get("event"):
                    if raw.get("event").split(".")[2] == self.CID:
                        self.onMessage(self, message)
            else:
                if not self.VERBOSE:
                    self.Logger.log(message, title = "Message Recieved")
                else:
                    self.Logger.log("No onMessage function set", title = "Error")

    def on_error(self, ws, error):
        self.Logger.log(error, title = "Error")
    
    def boot(self):
        if self.TOKEN is not None:
            params = {"token":self.TOKEN}
            value = self.request(self.ws,'auth.auth.authenticateBot',params=params,ind=LOGIN)
        else:
            params = {  "name":self.USERNAME,
                        "hash":self.HASH}
            value = self.request(self.ws,'auth.auth.login',params=params,ind=LOGIN)
        if "id" in value:
            if value.get("id") != LOGIN:
                raise LoginError(f"Invalid login response recieved {value}")
        if "error" in value:
            raise LoginError(f"Invalid login response recieved {value}")
        
        if self.TOKEN is not None:
            value = self.request(self.ws,'call.core.getBot',ind=GET_PLAYER)
        else:
            value = self.request(self.ws,'call.core.getPlayer',ind=GET_PLAYER)
        if "id" in value:
            if value.get("id") != GET_PLAYER:
                raise LoginError(f"Invalid login response recieved {value}")
        if "result" in value:
            if "rid" not in value.get("result"):
                raise LoginError(f"Invalid login response recieved {value}")
        self.RID = value.get("result").get("rid")
        try:
            self.CID = self.RID.split('.')[-1]
        except:
            raise LoginError(f"Invalid login response recieved {value}")

        value = self.request(self.ws,"get."+self.RID,ind=GET_CHARS)
        if self.TOKEN is not None:
            pass
        else:
            characters = []
            #Grab the char data to search to ID the bot
            if "result" in value:
                if "collections" in value["result"]:
                    if self.RID+".chars" in value["result"]["collections"]:
                        chars = value["result"]["collections"][self.RID+".chars"]
            try:        
                chars = [a['rid'] for a in chars] #Get the actual refs
                for ch in chars:
                    #Loop over the chars
                    char_data = value["result"]["models"][ch]
                    characters.append(char_data["name"] + " " + char_data["surname"] + " : " + char_data['id'])
                    if char_data["name"] == self.BOTFIRSTNAME and char_data["surname"] == self.BOTLASTNAME:
                        #If find the bot's name, get its ID and make the char object
                        self.CID = char_data["id"]
                if self.VERBOSE:
                    self.Logger.log(*characters, title = "Characters")
            except:
                raise LoginError(f"Invalid login response recieved {value}")
        

        method = "call."+self.RID+".controlChar"
        value = self.request(self.ws,method,params={'charId':self.CID},ind=CTRL_BOT)

        method = "call.core.char."+self.CID+".ctrl.wakeup"
        value = self.request(self.ws,method,ind=WAKEUP)

        value = self.request(self.ws,"subscribe."+self.RID,ind=GET_CHARS)

        if self.onOpen is not None:
            self.onOpen(self)
        else:
            self.Logger.log("No onOpen function set", title = "Error")


    def on_open(self, ws):
        # run the boot sequence in a seperate thread
        self.Logger.log("### opened ###", title = "Connection")
        boot = threading.Thread(target=self.boot)
        boot.start()

    def on_close(self, ws):
        self.Logger.log("### closed ###", title = "Connection")
    
    def run(self):
        self.ws = websocket.WebSocketApp (self.HOST,
                                        on_message  = self.on_message,
                                        on_error    = self.on_error,
                                        on_close    = self.on_close,
                                        on_open     = self.on_open,
                                    )
    
    def run_forever(self):
        if self.ws is None:
            self.run()
        self.ws.run_forever(origin=self.ORIGIN)

    def sleep(self):
        method = "call.core.char."+self.CID+".ctrl.sleep"
        self.send(self.ws,method,params={},ind=SLEEP)

    def say(self, msg):
        method = "call.core.char."+self.CID+".ctrl.say"
        self.send(self.ws,method,params={'msg':msg},ind=SAY)

    def go(self, exit):
        method = "call.core.char."+self.CID+".ctrl.useExit"
        self.send(self.ws,method,params={'exitId':exit.split(".")[-1]},ind=GO)

    def pose(self, msg):
        method = "call.core.char."+self.CID+".ctrl.pose"
        self.send(self.ws,method,params={'msg':msg},ind=POSE)

    def teleport(self,nodeId):
        method = "call.core.char."+self.CID+".ctrl.teleport"
        self.send(self.ws,method,params={'nodeId':nodeId},ind=TELEPORT)

    def whisper(self, target, msg, pose='whispers'):
        if type(target) == str:
            target = Character(self, id = target)
        method = "call.core.char."+self.CID+".ctrl.whisper"
        self.send(self.ws,method,params={'msg':msg,'charId':target.id,'pose':pose},ind=WHISPER)

    def address(self, target, msg):
        if type(target) == str:
            target = Character(self, id = target)
        method = "call.core.char."+self.CID+".ctrl.address"
        self.send(self.ws,method,params={'msg':msg,'charId':target.id},ind=ADDRESS)

    def message(self, target, msg):
        if type(target) == str:
            target = Character(self, id = target)
        method = "call.core.char."+self.CID+".ctrl.message"
        self.send(self.ws,method,params={'msg':msg,'charId':target.id},ind=MESSAGE)

    def ping(self):
        method = "call.core.char."+self.CID+".ctrl.ping"
        self.send(self.ws,method,params={},ind=PING)
    
    def getCharID(self, name):
        method = "call."+self.RID+".getChar"
        result = self.request(self.ws, method, params={"charName": name})
        if "result" in result:
            return result["result"]["rid"].split(".")[-1]
        elif "error" in result:
            if result["error"]["code"] == 'core.charNotFound':
                return None
            else:
                raise Exception(result["error"]["message"])
    
    def quit(self):
        self.sleep()
        self.ws.close()

if __name__ == "__main__":
    bot = Bot(USERNAME="<Your Username>", PASSWORD="<Your Password>", BOTFIRSTNAME="<Your Bot's First Name>", BOTLASTNAME="<Your Bot's Last Name>", VERBOSE=True)
    bot.onMessage = lambda msg: print("----"*10 + str(msg))
    bot.run()
    bot.run_forever()
