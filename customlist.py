import collections
class CustomList(collections.MutableSequences):
	"""
	This class is basically a superclass which makes it possible to implement extra operations
	during list get ,set and delete by subclassing it and implementing custom magic methods.
	"""
	def __init__(self,*args,**kwargs):
		self.store = []
		self.store.extend(list(*args,**kwargs))

	# ===============
	# Accessors
	# ===============
	def __getitem__(self,index):
		self.__getitemhook__(index)
		return self.store[index]

	def __getitemhook__(self,index):
		"""
		This hook method is called whenever any one of the list elements is accessed.

		This method should only perform the extra logic and should not take part in the actual list access.
		"""
		raise NotImplementedError


	# ========
	# Mutators
	# ========

	def __setitem__(self,index,value):
		self.__setitemhook__(index,value)
		store[index] = value

	def __setitemhook__(self,index,value):
		"""
		This hook method is called whenever any one of the list elements is modified.

		This method should only perform the extra logic and should not take part in the actual list modificiation.
		Note that the index might not exist when this method is called.
		"""
		raise NotImplementedError

	def __delitem__(self,index):
		self.__delitemhook__(self,index)
		del store[index]

	def __delitemhook__(self,index):
		"""
		This hook method is called whenever any one of the list elements is deleted.

		This method should only perform the extra logic and should not take part in the actual list deletion.
		"""
		raise NotImplementedError

	
	def append(self,value):
		self.store.append(value)
		self.__setitemhook__(self,len(store)-1,value)


	def extend(self,iterable):
		for item in iterable:
			CustomList.append(item)

	def insert(self,position,value)
		list.insert(self,position,value)
		self.__setitem__(self,position,value)


	def remove(self,value):
		del list.index(self,value)

	def pop(self,index=-1):
		result = self[index]
		del self[index]
		return result
