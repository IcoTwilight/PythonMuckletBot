import websocket
import json
import time
import threading
from Mucklet.log import Logger


class Request:
	iteration = 0
	time_out_period = 10
	
	def __init__(self, _connection, *method, notification: bool = False, **params):
		self.connection = _connection
		Request.iteration += 1
		self.id = Request.iteration
		
		self.params = params or {}
		if not method:
			self.method = ""
		else:
			self.method = ".".join(method)
		self.pending_data = {"jsonrpc": "2.0",
		                     "method" : self.method,
		                     "params" : self.params, }
		
		self.notification = notification
		
		# if the request is a notification (i.e. it does not require a response)
		if not self.notification:
			self.pending_data.update({"id": self.id})
		
		self.received_data = None
		self.sent_data = None
		self.sent_time = None
		self.recieved_time = None
		self.timed_out = False
	
	def send(self) -> "Request":
		if self.sent_data:
			self.connection.log_error("Message has already been sent")
			return self
		if self.received_data:
			self.connection.log_error("Message has already been received")
			return self
		if not self.connection.running:
			self.connection.log_error("Connection is not running")
			return self
		
		if not self.notification:
			# add the message to the promises
			self.connection.promises[self.id] = self
		# send the message
		self.connection.ws.send(json.dumps(self.pending_data))
		self.sent_data = self.pending_data.copy()
		self.sent_time = time.time()
		Logger.log_if_not_shown(f"Delivered - {self.sent_data}", (100, 200, 100))
		return self
	
	def resend(self) -> None:
		self.sent_data = None
		self.received_data = None
		self.send()
	
	def receive(self, data: dict) -> None:
		self.received_data = data.copy()
		self.pending_data = None
		# remove the message from the promises
		self.kill()
		self.recieved_time = time.time()
		
	def wait(self, time_out_period: int = None) -> "Request":
		if self.sent_data is None:
			# send the message
			self.send()
		time_out_period = time_out_period or Request.time_out_period
		# while the message has not timed out
		while time.time() - self.sent_time < time_out_period:
			# if the message has been received
			if self.received_data:
				# return self
				return self
			# sleep for 0.1 seconds
			time.sleep(0.1)
		# if the message has timed out
		self.connection.log_error(f"Message {self.id} has timed out", False)
		self.timed_out = True
		return self
	
	def __str__(self) -> str:
		ping = (self.recieved_time - self.sent_time) * 1000 if self.recieved_time else None
		ping = f"{ping:.2f}" if ping else "N/A"
		if self.received_data:
			return f"Message {self.id} [{ping}ms]:\n   --> {self.sent_data}\n   <-- {self.received_data}"
		if self.sent_data:
			return f"Message {self.id}: sent - {self.sent_data}, not received"
		return f"Message {self.id}: not sent, not received"
	
	def kill(self) -> None:
		try:
			self.connection.promises.pop(self.id)
		except KeyError:
			self.connection.log_error(f"Message {self.id} has already been killed", False)
	
	def value(self) -> dict:
		if not self.received_data:
			self.connection.log_error(f"Message {self.id} has not been received, now waiting for the data", False)
			self.wait()
		return self.received_data


class Cache:
	def __init__(self, client: "ResClient", data: any = None):
		self.client = client
		if data:
			self.data = data
		else:
			self.data = {}
		
		self.errored = set()
	
	def get(self, *rids: str, default: any = None) -> any:
		# follow the keys to the end, if there is a rid then start from the head with the rid and continue
		
		position = self.data
		for rid in rids:
			try:
				position = position[rid]
				if type(position) is dict and "rid" in position:
					position = self.get(position["rid"])
			except KeyError:
				if rid in self.errored:
					return default
				# we can try and subscribe to the resource
				resource = self.client.subscribe(rid).wait()
				if "error" in resource.value():
					self.errored.add(rid)
					return default
				try:
					position = self.get(rid)
				except KeyError:
					self.client.log_error(rid)
					self.client.log_error(str(resource))
					return default
		
		return position
	
	def set(self, rid: str, value: any) -> None:
		self.data[rid] = value
	
	def change(self, rid: str, values: dict) -> None:
		for key, value in values.items():
			if value == {"action": "delete"}:
				self.data[rid].pop(key)
			else:
				self.data[rid][key] = value
	
	def add(self, rid: str, index: int, value: dict) -> None:
		self.data.get(rid).insert(index, value)
	
	def remove(self, rid: str, index: int) -> None:
		self.data.get(rid).pop(index)
	
	def __getitem__(self, item: any) -> any:
		return self.get(item)
	
	def __setitem__(self, key: str, value: any) -> None:
		self.set(key, value)
	
	def __delitem__(self, key: str) -> None:
		self.data.pop(key)
	
	def __str__(self) -> str:
		return str(self.data)
	
	def __repr__(self) -> str:
		return str(self.data)

	def __contains__(self, item: str) -> bool:
		return item in self.data


class Connection:
	def __init__(self, host: str, origin: str):
		self.host = host
		self.origin = origin
		self.ws = websocket.WebSocketApp(self.host,
		                                 on_message = self.on_message,
		                                 on_error = self.on_error,
		                                 on_close = self.on_close,
		                                 on_open = self.on_open, )
		self.running = False
		self.promises = {}
		self.log_info = Logger(format_color = (80, 80, 210), bold = False)
		self.log_error = Logger(format_color = (210, 80, 80), bold = False)
		self.log_success = Logger(format_color = (80, 210, 80), bold = False)
		
		self.on_events = {
			"message": lambda message: self.log_info(f"Received - {message}", False),
			"error"  : lambda error: self.log_error(f"Error - {error}", False),
			"close"  : lambda: self.log_info("Connection closed", False),
			"open"   : lambda: self.log_info("Connection opened", False),
		}
		
	def connect(self) -> "Connection":
		def run_forever():
			self.ws.run_forever(origin = self.origin)
		
		threading.Thread(target = run_forever).start()
		while not self.running:
			time.sleep(0.1)
		return self
	
	def on_message(self, ws, message):
		message = json.loads(message)
		if "id" in message:
			if message["id"] in self.promises:
				self.promises[message["id"]].receive(message)
			else:
				self.log_error(f"Recieved message with id {message['id']} that was not sent by this client", False)
		threading.Thread(target = self.on_events["message"], args = (message,)).start()
		
	def on_error(self, ws, error):
		threading.Thread(target = self.on_events["error"], args = (error,)).start()
	
	def on_close(self, ws):
		self.running = False
		threading.Thread(target = self.on_events["close"]).start()
	
	def on_open(self, ws):
		self.running = True
		threading.Thread(target = self.on_events["open"]).start()
	
	def request(self, *args, notification = False, **kwargs) -> Request:
		return Request(self, *args, **kwargs, notification = notification)
	
	def emulate(self, **message) -> None:
		if "id" in message:
			if message["id"] in self.promises:
				self.promises[message["id"]].receive(message)
			else:
				self.log_error(f"Recieved message with id {message['id']} that was not sent by this client", False)
		threading.Thread(target = self.on_events["message"], args = (message,)).start()


class ResClient(Connection):
	def __init__(self, host: str, origin: str):
		super().__init__(host, origin)
		
		self.cache = Cache(self)
		self.cache.head = self.cache

	def on_message(self, ws, response):
		response = json.loads(response)
		if "id" in response:
			if response["id"] in self.promises:
				self.promises[response["id"]].receive(response)
			else:
				self.log_error(f"Recieved message with id {response['id']} that was not sent by this client", False)
		self.process_response(response)

	def process_response(self, response: dict) -> None:
		Logger.log_if_not_shown(str(response))
		
		if "result" in response:
			result = response.get("result", {})
			if "models" in result:
				self.cache_dict(result.get("models", {}))
				
			if "collections" in result:
				self.cache_dict(result.get("collections", {}))
			
			if "errors" in result:
				self.display_errors(result.get("errors", {}))
		
		if "data" in response:
			data = response.get("data", {})
			if "models" in data:
				self.cache_dict(data.get("models", {}))
			
			if "collections" in data:
				self.cache_dict(data.get("collections", {}))
			
			if "errors" in data:
				self.display_errors(data.get("errors", {}))
		
		if "event" in response:
			if "data" not in response:
				self.log_error(f"Event {response['event']} did not contain any data", False)
				return
			data = response.get("data", {})
			event = response.get("event", {}).split(".")
			rid = ".".join(event[:-1])
			event = event[-1]
			
			if event == "change":
				self.cache.change(rid, data.get("values", {}))
			
			if event == "add":
				self.cache.add(rid, data.get("idx", 0), data.get("value", {}))
			
			if event == "remove":
				self.cache.remove(rid, data.get("idx", 0))
			
			if event in ["add", "change", "create", "delete", "patch", "reset", "reaccess", "remove", "unsubscribe"]:
				return
			
			else:
				threading.Thread(target = self.on_events["message"], args = (response,)).start()
	
	def display_errors(self, errors: dict) -> None:
		for service, error in errors.items():
			self.log_error(f"{service} - {error.get('code')} - {error.get('message')}", False)
	
	def cache_dict(self, values: dict) -> None:
		for rid, value in values.items():
			self.cache.set(rid, value)
	
	def version(self, protocol: str) -> Request:
		"""
		Version request
			method: version
			
			Version requests are sent by the client to tell which RES protocol
			version it supports, and to get information on what protocol version
			the gateway supports.
			
			The request SHOULD be the first request sent by the client after an
			established connection.
			
			If not sent, or if the protocol property is omitted in the request,
			the gateway SHOULD assume version v1.1.x.
			
			Parameters
				The request parameters are optional.
				If not omitted, the parameters object SHOULD have the following
				property:
			
				protocol
					The RES protocol version supported by the client.
					MUST be a string in the format "[MAJOR].[MINOR].[PATCH]". Eg. "1.2.3".
			
			Result
				protocol
					The RES protocol version supported by the gateway.
					MUST be a string in the format "[MAJOR].[MINOR].[PATCH]". Eg. "1.2.3".
			
			Error
				A system.unsupportedProtocol error response will be sent if the gateway
				cannot support the client protocol version.
				A system.invalidRequest error response will be sent if the gateway only
				supports RES Protocol v1.1.1 or below, prior to the introduction of the
				version request.
		"""
		return self.request("version", protocol = protocol)
	
	def subscribe(self, *rid):
		"""
		Subscribe request
			method: subscribe.<resourceID>
			
			Subscribe requests are sent by the client to subscribe to a resource.
			The request has no parameters.
			
			Result
				models
					Resource set models.
					May be omitted if no new models were subscribed.
				
				collections
					Resource set collections.
					May be omitted if no new collections were subscribed.
				
				errors
					Resource set errors.
					May be omitted if no subscribed resources encountered errors.
			
			Error
				An error response will be sent if the resource couldn't be subscribed to.
				Any resource reference that fails will not lead to an error response, but
				the error will be added to the resource set errors.
		"""
		return self.request("subscribe", *rid)
	
	def unsubscribe(self, *rid, count = 1):
		"""
		Unsubscribe request
			method: unsubscribe.<resourceID>
			
			Unsubscribe requests are sent by the client to unsubscribe to previous direct
			subscriptions.
			
			The resource will only be considered unsubscribed when there are no more direct
			or indirect subscriptions.
			
			If the count property is omitted in the request, the value of 1 is assumed.
			
			
			Parameters
				The request parameters are optional.
				If not omitted, the parameters object SHOULD have the following property:
			
				count
					The number of direct subscriptions to unsubscribe to.
					MUST be a number greater than 0.
				
			Result
				The result has no payload.
			
			Error
				An error response with code system.noSubscription will be sent if the
				resource has no direct subscription, or if count exceeds the number of
				direct subscriptions. If so, the number of direct subscriptions will be
				unaffected.
		"""
	
	def get(self, *rid):
		"""
		Get requests are sent by the client to get a resource without making a subscription.
		
		method: get.<resourceID>
		
		Parameters
			The request has no parameters.
		
		Result
			models
				Resource set models.
				May be omitted if no new models were retrieved.
			
			collections
				Resource set collections.
				May be omitted if no new collections were retrieved.
			
			errors
				Resource set errors.
				May be omitted if no retrieved resources encountered errors.
		
		Error
			An error response will be sent if the resource couldn't be retrieved.
			Any resource reference that fails will not lead to an error response, but the
			error will be added to the resource set errors.
		"""
		return self.request("get", *rid)
	
	def call(self, *rid: str, **kwargs):
		"""
		Call request
			method: call.<resourceID>.<resourceMethod>
			
			Call requests are sent by the client to invoke a method on the resource.
			The response may either contain a result payload or a resource ID.
			
			In case of a resource ID, the resource is considered directly subscribed.
			
			Parameters
				The request parameters are defined by the service.
			
			Result
				The result is an object with the following members:
				
				payload
					Result payload as defined by the service.
					MUST be omitted if rid is set.
					MUST NOT be omitted if rid is not set.
				
				rid
					Resource ID of subscribed resource.
					MUST be omitted if payload is set.
				
				models
					Resource set models.
					May be omitted if no new models were subscribed.
					MUST be omitted if payload is set.
				
				collections
					Resource set collections.
					May be omitted if no new collections were subscribed.
					MUST be omitted if payload is set.
				
				errors
					Resource set errors.
					May be omitted if no subscribed resources encountered errors.
					MUST be omitted if payload is set.
			
			Error
				An error response will be sent if the method couldn't be called,
				or if the method was called, but an error was encountered.
		"""
		return self.request("call", *rid, **kwargs)
	
	def auth(self, *rid, **params):
		"""
		Auth request
		method: auth.<resourceID>.<resourceMethod>
		
		Auth requests are sent by the client to authenticate the client connection.
		The response may either contain a result payload or a resource ID.
		
		In case of a resource ID, the resource is considered directly subscribed.
		
		Parameters
			The request parameters are defined by the service.
		
		Result
			The result is an object with the following members:
			
			payload
				Result payload as defined by the service.
				MUST be omitted if rid is set.
				MUST NOT be omitted if rid is not set.
			
			rid
				Resource ID of subscribed resource.
				MUST be omitted if payload is set.
			
			models
				Resource set models.
				May be omitted if no new models were subscribed.
				MUST be omitted if payload is set.
			
			collections
				Resource set collections.
				May be omitted if no new collections were subscribed.
				MUST be omitted if payload is set.
		Error
			An error response will be sent if the resource could not be created,
			or if an error was encountered retrieving the newly created resource.
		"""
		return self.request("auth", *rid, **params)
	
	def on(self, event: str):
		if event not in self.on_events:
			self.log_error(f"Event '{event}' is not supported. Supported events are: {', '.join(self.on_events)}")
			return
		
		def decorator(func):
			self.on_events[event] = func
			return func
		
		return decorator
	
	def close(self):
		self.ws.close()
		self.promises.clear()
	
	def new(self):
		cls = self.__class__
		result = cls(self.host, self.origin)
		return result
