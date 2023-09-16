import os
from ast import literal_eval as load


class Storage:
	def __init__(self, name):
		self.name = name
	
	def __getitem__(self, key):
		try:
			# check if the file is a folder
			if os.path.isdir(os.path.join(self.name, key)):
				# if it is, return a CachedDictionary
				return CachedDictionary(f"{os.path.join(self.name, key)}")
			with open(os.path.join(self.name, key), "r") as f:
				value = load(f.read())
				if type(value) == dict:
					# delete the file
					os.remove(os.path.join(self.name, key))
					# if the value is a dict, return a CachedDictionary
					return CachedDictionary(f"{os.path.join(self.name, key)}", **value)
		except FileNotFoundError:
			raise KeyError(f"Key {key} not found in storage {self.name}")
	
	def __setitem__(self, key, value):
		# check if the file/directory exists
		if not os.path.exists(self.name):
			# if not, create it
			os.mkdir(self.name)
		
		if type(value) == dict:
			# if the value is a dict, save it to a CachedDictionary
			value = CachedDictionary(f"{self.name}\\{key}", **value)
			return
		
		# write the value to the file
		with open(os.path.join(self.name, key), "w") as f:
			f.write(repr(value))
	
	def __delitem__(self, key):
		try:
			os.remove(os.path.join(self.name, key))
		except FileNotFoundError:
			raise KeyError(f"Key {key} not found in storage {self.name}")
	
	def __contains__(self, key):
		return os.path.exists(os.path.join(self.name, key))
	
	def __iter__(self):
		# check if the storage exists
		if not os.path.exists(self.name):
			# if not, return an empty list
			return iter([])
		return iter(os.listdir(self.name))
	
	def __len__(self):
		# check if the storage exists
		if not os.path.exists(self.name):
			# if not, return an empty list
			return 0
		return len(os.listdir(self.name))
	
	def __repr__(self):
		return f"Storage({self.name}) - {self.keys()}"
	
	def __str__(self):
		return f"Storage({self.name}) - {self.keys()}"
	
	def get(self, key, default = None):
		try:
			return self[key]
		except KeyError:
			return default
	
	def keys(self):
		# check if the storage exists
		if not os.path.exists(self.name):
			# if not, return an empty list
			return []
		return os.listdir(self.name)
	
	def values(self):
		return [self[key] for key in self.keys()]
	
	def items(self):
		return zip(self.keys(), self.values())
	
	def clear(self):
		for key in self.keys():
			del self[key]
	
	def pop(self, key, default = None):
		value = self.get(key, default)
		del self[key]
		return value


class CachedDictionary(dict):
	def __init__(self, name, **kwargs):
		super().__init__(**kwargs)
		self.storage = Storage(name)
	
	def __getitem__(self, key):
		# check if key is in dict
		if key not in super().keys():
			# if not, get it from storage and cache it
			super().__setitem__(key, self.storage[key])
		
		# check if the value is a dict
		if type(super().__getitem__(key)) == dict:
			# if the value is a dict, return a CachedDictionary
			return CachedDictionary(f"{os.path.join(self.storage.name, key)}", **super().__getitem__(key))
		# if the value is not a dict, return the value
		return super().__getitem__(key)
	
	def __setitem__(self, key, value):
		# set the value in the storage
		self.storage[key] = value
		
		if type(value) == dict:
			# if the value is a dict, save it to a CachedDictionary
			value = CachedDictionary(f"{self.storage.name}\\{key}", **value)
		
		# set the value in the dict
		super().__setitem__(key, value)
	
	def __delitem__(self, key):
		# delete the value from the dict
		super().__delitem__(key)
		# delete the value from the storage
		del self.storage[key]
	
	def __contains__(self, key):
		return key in super().keys() or key in self.storage
	
	def __iter__(self):
		return iter(self.storage)
	
	def __len__(self):
		return len(self.storage)
	
	def __repr__(self):
		return f"CachedDictionary({self.storage.name}) - {self.keys()}"
	
	def __str__(self):
		return f"CachedDictionary({self.storage.name}) - {self.keys()}"
	
	def get(self, key, default = None):
		try:
			return self[key]
		except KeyError:
			return default
	
	def keys(self):
		return self.storage.keys()
	
	def values(self):
		return self.storage.values()
	
	def items(self):
		return self.storage.items()
	
	def clear(self):
		super().clear()
		self.storage.clear()
	
	def pop(self, key, default = None):
		value = self.get(key, default)
		del self[key]
		return value
	
	def save(self):
		# save all the values in the cache to the storage
		for key, value in self.items():
			self.storage[key] = value
	
	def load(self):
		# load all the values from the storage to the cache
		for key in self.storage.keys():
			self[key] = self.storage[key]
	
	def sync(self):
		# sync the cache and the storage
		self.save()
		self.load()


if __name__ == "__main__":
	test_storage = CachedDictionary("test")
	test_storage["test"] = {"test": "test"}
	print(test_storage["test"])
