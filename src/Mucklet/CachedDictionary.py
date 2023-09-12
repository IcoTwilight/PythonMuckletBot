import bson
import os


class KeyNotFoundError(OSError):
	""" Key not found within a Cached Dictionary. """
	
	def __init__(self, *args, **kwargs):
		pass


class CachedObject:
	def __init__(self, cached_dict: "CachedDictionary", key, data):
		self.root = cached_dict
		self.key = str(key)
		self.data = data.copy()
	
	def __update__(self):
		self.root[self.key] = self.data.copy()
	
	def __setitem__(self, key, value):
		self.data[key] = value
		self.__update__()
	
	def __delitem__(self, key):
		del self.data[key]
		self.__update__()
		
	def __getitem__(self, key):
		return self.data[key]
	
	def clear(self) -> None:
		self.data.clear()
		self.__update__()
	
	def get(self, key, default = None):
		return self.data.get(str(key), default)
	
	def set(self, key, value):
		self[key] = value
	
	def __str__(self):
		return str(self.data)
	
	def __repr__(self):
		return repr(self.data)
	

class CachedDictionary:
	def __init__(self, name_space):
		self.name_space = name_space
		self.cache = {}
		self.keys_cache = self.__get_keys__()
		# if the storage doesn't exist
		if not self.__name_space_exists__():
			# create the storage
			self.__create_name_space__(name_space)
	
	@staticmethod
	def __get_file_name__(key):
		return f"{key}.bson"
	
	def __get_from_storage__(self, key, default = None, raise_error = True):
		# check if the file exists
		if not os.path.exists(os.path.join(self.name_space, self.__get_file_name__(key))):
			if raise_error:
				raise KeyNotFoundError(key)
			else:
				return default
		# load the file
		with open(os.path.join(self.name_space, self.__get_file_name__(key)), 'rb') as f:
			# return the loaded file as a dictionary
			return bson.loads(f.read())
	
	def __test_get_from_storage__(self, key, default = None):
		# get the key from the storage
		print("Getting key from storage...")
		value = self.__get_from_storage__(key, default, True)
		print(f"Got {value} from storage!")
	
	def __set_to_storage__(self, key, value):
		# dump the value to a file
		with open(os.path.join(self.name_space, self.__get_file_name__(key)), 'wb') as f:
			f.write(bson.dumps(value))
	
	def __test_set_to_storage__(self, key, value):
		# set the key to the storage
		print("Setting key to storage...")
		self.__set_to_storage__(key, value)
		print("Set key to storage!")
	
	def __remove_from_storage__(self, key):
		# check if the file exists
		if not os.path.exists(os.path.join(self.name_space, self.__get_file_name__(key))):
			raise KeyNotFoundError(key)
		# remove the file
		os.remove(os.path.join(self.name_space, self.__get_file_name__(key)))
	
	def __test_remove_from_storage__(self, key):
		# remove the key from the storage
		print("Removing key from storage...")
		self.__remove_from_storage__(key)
		print("Removed key from storage!")
	
	def __clear_storage__(self):
		# get all the files from the storage
		file_names = {key for key in os.listdir(self.name_space)}
		# remove all the files from the storage
		for file_name in file_names:
			os.remove(os.path.join(self.name_space, file_name))
	
	def __test_clear_storage__(self):
		# clear the storage
		print("Clearing storage...")
		self.__clear_storage__()
		print("Cleared storage!")
	
	def __delete_name_space__(self):
		# delete the storage
		os.rmdir(self.name_space)
	
	def __test_delete_name_space__(self):
		# delete the storage
		print("Deleting storage...")
		self.__delete_name_space__()
		print("Deleted storage!")
	
	def __get_keys__(self):
		# check if the storage exists
		if not os.path.exists(self.name_space):
			# create the storage
			os.mkdir(self.name_space)
		# get all the files from the storage
		file_names = {key for key in os.listdir(self.name_space)}
		# convert the file names to keys and return them
		return {".".join(file_name.split(".")[:-1]) for file_name in file_names}
	
	def __test_get_keys__(self):
		# get the keys from the storage
		print("Getting keys from storage...")
		keys = self.__get_keys__()
		print(f"Got {keys} from storage!")
	
	@staticmethod
	def __create_name_space__(name_space):
		# create the storage
		os.mkdir(name_space)
	
	def __name_space_exists__(self):
		# check if the storage exists
		return os.path.exists(self.name_space)
	
	def __getitem__(self, key):
		# check if the key is in the cache
		if str(key) in self.cache:
			if isinstance(self.cache[str(key)], CachedObject):
				return self.cache[str(key)]
			return CachedObject(self, str(key), self.cache[str(key)])
		# get the key from the storage
		value = self.__get_from_storage__(str(key), raise_error = True)
		# add the key to the cache for quicker lookup
		self.cache[str(key)] = CachedObject(self, str(key), value)
		return CachedObject(self, str(key), value)
	
	def __get_raw__(self, key):
		if str(key) in self.cache:
			return self.cache[str(key)]
	
	def __test_getitem__(self, key):
		# get the key from the storage
		print("Getting key from storage...")
		value = self.__getitem__(key)
		print(f"Got {value} from storage!")
	
	def __setitem__(self, key, value):
		if isinstance(value, CachedObject):
			value = value.data
		# set the key to the storage
		self.__set_to_storage__(str(key), value)
		# set the key to the cache
		self.cache[str(key)] = value
		# add the key to the keys
		self.keys_cache.add(str(key))
	
	def __test_setitem__(self, key, value):
		# set the key to the storage
		print("Setting key to storage...")
		self.__setitem__(key, value)
		print("Set key to storage!")
	
	def __delitem__(self, key):
		# remove the key from the cache
		del self.cache[str(key)]
		# remove the key from the keys
		self.keys_cache.remove(str(key))
		# remove the key from the storage
		self.__remove_from_storage__(str(key))
	
	def __test_delitem__(self, key):
		# remove the key from the storage
		print("Removing key from storage...")
		self.__delitem__(key)
		print("Removed key from storage!")
	
	def __contains__(self, key):
		# check if the key is in the keys
		return str(key) in self.keys_cache
	
	def __test_contains__(self, key):
		# check if the key is in the storage
		print("Checking if key is in storage...")
		contains = key in self
		print(f"Checked if key is in storage! {contains}")
	
	def clear(self):
		# clear the cache
		self.cache.clear()
		# clear the keys
		self.keys_cache.clear()
		# clear the storage
		self.__clear_storage__()
	
	def __test_clear__(self):
		# clear the storage
		print("Clearing storage...")
		self.clear()
		print("Cleared storage!")
	
	def get(self, key, default = None):
		try:
			return self[key]
		except KeyNotFoundError:
			return default
	
	def __test_get__(self, key, default = None):
		# get the key from the storage
		print("Getting key from storage...")
		value = self.get(key, default)
		print(f"Got {value} from storage!")
	
	def keys(self):
		# return the keys
		return self.keys
	
	def __test_keys__(self):
		# get the keys from the storage
		print("Getting keys from storage...")
		keys = self.keys
		print(f"Got {keys} from storage!")


if __name__ == '__main__':
	dictionary = CachedDictionary("CachedDictionary Test")
	dictionary["test"] = {"test": "test1"}
	
	#result = dictionary["test"]
	#print(result)
	
	#result["test"] = "test2"
	#print(result)
	
	result = dictionary["test"]
	print(result)

# TODO: Implement the following methods:
# clear
# copy
# fromkeys
# get ------- Done
# items
# keys ------ Done
# pop
# popitem
# setdefault
# update
# values

# Let's be honest Ico, this is good enough for now. Good job :) - Omi
