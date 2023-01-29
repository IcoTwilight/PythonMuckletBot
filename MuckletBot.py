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

class Player:
    def __init__(self, USERNAME, PASSWORD, BOTFIRSTNAME, BOTSURNAME, HOST = 'wss://api.test.mucklet.com', ORIGIN = 'https://test.mucklet.com', VERBOSE = False):
        self.USERNAME = USERNAME
        self.PASSWORD = PASSWORD
        self.BOTFIRSTNAME = BOTFIRSTNAME
        self.BOTSURNAME = BOTSURNAME
        self.HOST = HOST
        self.ORIGIN = ORIGIN
        self.VERBOSE = VERBOSE
        self.BOTNAME = (BOTFIRSTNAME, BOTSURNAME)
        self.pepper = "TheStoryStartsHere"
        m = hashlib.sha256()
        m.update(bytes(self.PASSWORD,'UTF-8'))
        hx = m.hexdigest()
        self.PASS = codecs.encode(codecs.decode(hx, 'hex'), 'base64').decode()[:-1]
        hx = hmac.new(bytes(self.pepper,'UTF-8'),msg=bytes(self.PASSWORD,'UTF-8'), digestmod = hashlib.sha256).hexdigest()
        self.HASH = codecs.encode(codecs.decode(hx, 'hex'), 'base64').decode()[:-1]
        self.ws = None # gets set to the websocket object in the on_open method when the websocket is opened.
        self.bootIndex = 0
        self.CID = None # The character ID of the bot we will control, set in the on_message method when we get the character list.
        self.RID = None # The room ID of the room we will be in, set in the on_message method when we get the character list.
        self.OnMessage = None # This is a function that takes a message as a parameter and is set by the user. It is called in the on_message method.
        self.OnStart = None # This is a function that takes no parameters and is set by the user. It is called once after the bot has booted. will be run in a thread.

    def send(self, ws,method,ind=0,params = None):
        #Helper function to wrap WS function
        request = {"id":ind,"method":method,"params":params}
        msg = json.dumps(request)
        ws.send(msg)
        if self.VERBOSE:
            print("sent: ",msg)
            print("--------")

    def on_message(self, ws, message):
        #Message handler- basically everything taps here
        msg = json.loads(message) #make it a dictionary

        #Be loud?
        if self.VERBOSE:
            print("recieved: ",msg)
            print("--------")

        #Error message handler- currently just to pass boot if already controlled or awake
        if 'error' in msg and self.bootIndex < 6:
            if self.bootIndex == 3 and msg['id'] == CTRL_BOT:
                self.bootIndex = 4
            if self.bootIndex == 4 and msg['id'] == WAKEUP:
                self.bootIndex = 5
        elif 'error' in msg:
            #Prints errors outside boot cycle
            print(msg)

        #For reply responses
        if 'result' in msg and self.bootIndex < 7:

            #Boot Cycle syncing
            #The login and setup are only allowed to proceed once each
            #  requested message arrives, and is processed
            if self.bootIndex == 1 and msg["id"] == LOGIN:
                self.bootIndex = 2
            if self.bootIndex == 2 and msg["id"] == GET_PLAYER:
                self.RID = msg['result']['rid']
                self.bootIndex = 3
            if self.bootIndex == 3 and msg['id'] == GET_CHARS:
                #Grab the char data to search to ID the bot
                chars = msg["result"]["collections"][self.RID+".chars"]
                chars = [a['rid'] for a in chars] #Get the actual refs
                for ch in chars:
                    #Loop over the chars
                    char_data = msg["result"]["models"][ch]
                    print("    " + char_data["name"] + " " + char_data["surname"] + " : " + char_data['id'])
                    if char_data["name"] == self.BOTFIRSTNAME and char_data["surname"] == self.BOTSURNAME:
                        #If find the bot's name, get its ID and make the char object
                        self.CID = char_data["id"]
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
                self.OnMessage(self, msg)
            else:
                print("No OnMessage function set.")
                print("It Would Recieve: ", msg)
        

    def on_error(self, ws, error):
        #Helper function to wrap WS function
        if self.VERBOSE:
            print("error: ",error)
            print("--------")

    def on_close(self, ws):
        #Helper function to wrap WS function
        if self.VERBOSE:
            print("### closed ###")
            print("--------")

    def on_open(self, ws):
        #Helper function to wrap WS function
        if self.VERBOSE:
            print("### opened ###")
            print("--------")
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
        print("AUTHENTICATING")
        #Authenticate and get the player info
        params = {  "name":self.USERNAME,
                    "hash":self.HASH}
        self.send(self.ws,'auth.auth.login',params=params,ind=LOGIN)
        while (self.bootIndex == 1):
            time.sleep(0.1)

        print("GETTING PLAYER RID")
        #Get Player rid
        self.send(self.ws,'call.core.getPlayer',ind=GET_PLAYER)
        while(self.bootIndex == 2):
            time.sleep(0.1)

        print("GETTING CHARS SET")
        #Get character data
        self.send(self.ws,"get."+self.RID,ind=GET_CHARS)
        while(self.bootIndex == 3):
            time.sleep(0.1)

        print("CONTROLLING BOT")
        #Take control of the bot character
        method = "call."+self.RID+".controlChar"
        self.send(self.ws,method,params={'charId':self.CID},ind=CTRL_BOT)
        while(self.bootIndex == 4):
            time.sleep(0.1)

        print("WAKING BOT")
        #Wake the bot up
        method = "call.core.char."+self.CID+".ctrl.wakeup"
        self.send(self.ws,method,ind=WAKEUP)
        while(self.bootIndex == 5):
            time.sleep(0.1)

        print("GETTING CHAR DATA")
        #Get looking character data
        self.send(self.ws,"subscribe."+self.RID,ind=GET_CHARS)
        while(self.bootIndex == 6):
            time.sleep(0.1)

        #Done booting
        print("BOOTED")

        # If user has a boot function, call it in a new thread
        if self.OnStart != None:
            bootThread = threading.Thread(target=self.OnStart, args=(self,))
            bootThread.start()
        else:
            print("No OnBoot function set.")

    def gosleep(self):
        method = "call.core.char."+self.CID+".ctrl.sleep"
        self.send(self.ws,method,params={},ind=SLEEP)

    def say(self,msg):
        method = "call.core.char."+self.CID+".ctrl.say"
        self.send(self.ws,method,params={'msg':msg},ind=SAY)

    def go(self,ext):
        method = "call.core.char."+self.CID+".ctrl.useExit"
        self.send(self.ws,method,params={'exitId':ext.split(".")[-1]},ind=GO)

    def pose(self,msg):
        method = "call.core.char."+self.CID+".ctrl.pose"
        self.send(self.ws,method,params={'msg':msg},ind=POSE)

    def teleport(self,nodeId):
        method = "call.core.char."+self.CID+".ctrl.teleport"
        self.send(self.ws,method,params={'nodeId':nodeId},ind=TELEPORT)

    def whisper(self,msg,targetId,pose='whispers'):
        method = "call.core.char."+self.CID+".ctrl.whisper"
        self.send(self.ws,method,params={'msg':msg,'charId':targetId,'pose':pose},ind=WHISPER)

    def address(self,msg,targetId):
        method = "call.core.char."+self.CID+".ctrl.address"
        self.send(self.ws,method,params={'msg':msg,'charId':targetId},ind=ADDRESS)

    def message(self,msg,targetId):
        method = "call.core.char."+self.CID+".ctrl.message"
        self.send(self.ws,method,params={'msg':msg,'charId':targetId},ind=MESSAGE)

    def ping(self):
        method = "call.core.char."+self.CID+".ctrl.ping"
        self.send(self.ws,method,params={},ind=PING)



class Bot:
    def __init__(self, TOKEN, HOST = 'wss://api.test.mucklet.com', ORIGIN = 'https://test.mucklet.com', VERBOSE = False):
        self.TOKEN = TOKEN
        self.HOST = HOST
        self.ORIGIN = ORIGIN
        self.VERBOSE = VERBOSE
        self.ws = None # gets set to the websocket object in the on_open method when the websocket is opened.
        self.bootIndex = 0
        self.CID = None # The character ID of the bot we will control, set in the on_message method when we get the character list.
        self.RID = None # The room ID of the room we will be in, set in the on_message method when we get the character list.
        self.OnMessage = None # This is a function that takes a message as a parameter and is set by the user. It is called in the on_message method.
        self.OnStart = None # This is a function that takes no parameters and is set by the user. It is called once after the bot has booted. will be run in a thread.

    def send(self, ws,method,ind=0,params = None):
        #Helper function to wrap WS function
        request = {"id":ind,"method":method,"params":params}
        msg = json.dumps(request)
        ws.send(msg)
        if self.VERBOSE:
            print("sent: ",msg)
            print("--------")

    def on_message(self, ws, message):
        #Message handler- basically everything taps here
        msg = json.loads(message) #make it a dictionary

        #Be loud?
        if self.VERBOSE:
            print("recieved: ",msg)
            print("--------")

        #Error message handler- currently just to pass boot if already controlled or awake
        if 'error' in msg and self.bootIndex < 6:
            if self.bootIndex == 3 and msg['id'] == CTRL_BOT:
                self.bootIndex = 4
            if self.bootIndex == 4 and msg['id'] == WAKEUP:
                self.bootIndex = 5
        elif 'error' in msg:
            #Prints errors outside boot cycle
            print(msg)

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
                self.OnMessage(self, msg)
            else:
                print("No OnMessage function set.")
                print("It Would Recieve: ", msg)
        

    def on_error(self, ws, error):
        #Helper function to wrap WS function
        if self.VERBOSE:
            print("error: ",error)
            print("--------")

    def on_close(self, ws):
        #Helper function to wrap WS function
        if self.VERBOSE:
            print("### closed ###")
            print("--------")

    def on_open(self, ws):
        #Helper function to wrap WS function
        if self.VERBOSE:
            print("### opened ###")
            print("--------")
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
        print("AUTHENTICATING")
        #Authenticate and get the player info
        params = {"token":self.TOKEN}
        self.send(self.ws,'auth.auth.authenticateBot',params=params,ind=LOGIN)
        while (self.bootIndex == 1):
            time.sleep(0.1)

        print("GETTING PLAYER RID")
        #Get Player rid
        self.send(self.ws,'call.core.getBot',ind=GET_PLAYER)
        while(self.bootIndex == 2):
            time.sleep(0.1)

        print("GETTING CHARS SET")
        #Get character data
        self.send(self.ws,"get."+self.RID,ind=GET_CHARS)
        while(self.bootIndex == 3):
            time.sleep(0.1)

        print("CONTROLLING BOT")
        #Take control of the bot character
        method = "call."+self.RID+".controlChar"
        self.send(self.ws,method,params={'charId':self.CID},ind=CTRL_BOT)
        while(self.bootIndex == 4):
            time.sleep(0.1)

        print("WAKING BOT")
        #Wake the bot up
        method = "call.core.char."+self.CID+".ctrl.wakeup"
        self.send(self.ws,method,ind=WAKEUP)
        while(self.bootIndex == 5):
            time.sleep(0.1)

        print("GETTING CHAR DATA")
        #Get looking character data
        self.send(self.ws,"subscribe."+self.RID,ind=GET_CHARS)
        while(self.bootIndex == 6):
            time.sleep(0.1)

        #Done booting
        print("BOOTED")

        #Call user's OnStart function if it exists in a new thread
        if self.OnStart != None:
            onStartThread = threading.Thread(target=self.OnStart, args=(self,))
            onStartThread.start()
        else:
            print("No OnStart function set.")

    def gosleep(self):
        method = "call.core.char."+self.CID+".ctrl.sleep"
        self.send(self.ws,method,params={},ind=SLEEP)

    def say(self,msg):
        method = "call.core.char."+self.CID+".ctrl.say"
        self.send(self.ws,method,params={'msg':msg},ind=SAY)

    def go(self,ext):
        method = "call.core.char."+self.CID+".ctrl.useExit"
        self.send(self.ws,method,params={'exitId':ext.split(".")[-1]},ind=GO)

    def pose(self,msg):
        method = "call.core.char."+self.CID+".ctrl.pose"
        self.send(self.ws,method,params={'msg':msg},ind=POSE)

    def teleport(self,nodeId):
        method = "call.core.char."+self.CID+".ctrl.teleport"
        self.send(self.ws,method,params={'nodeId':nodeId},ind=TELEPORT)

    def whisper(self,msg,targetId,pose='whispers'):
        method = "call.core.char."+self.CID+".ctrl.whisper"
        self.send(self.ws,method,params={'msg':msg,'charId':targetId,'pose':pose},ind=WHISPER)

    def address(self,msg,targetId):
        method = "call.core.char."+self.CID+".ctrl.address"
        self.send(self.ws,method,params={'msg':msg,'charId':targetId},ind=ADDRESS)

    def message(self,msg,targetId):
        method = "call.core.char."+self.CID+".ctrl.message"
        self.send(self.ws,method,params={'msg':msg,'charId':targetId},ind=MESSAGE)

    def ping(self):
        method = "call.core.char."+self.CID+".ctrl.ping"
        self.send(self.ws,method,params={},ind=PING)
