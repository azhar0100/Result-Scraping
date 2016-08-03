class CustomList(list):
"""
This class is basically a decorator class which makes it possible to implement extra operations
during list get ,set and delete
"""

	def __init__(self,fn,*args,**kwargs):
		"""
		This method just executes the list __init__ method and the method provided as the decorator.

		Args:
			fn (function) : Function to which this class is applied as a decorator.
		"""

		list.__init__(self,*args,**kwargs):
		fn(self)

	def getter(self,fn):
		"""
		This is a decorator which is used to set the custom get function.
		Args:
			fn (function) : Function which takes two arguments , (self,key)
		"""
		self.get_func = fn
		return fn

	def __getitem__(self,key):
		"""
		This is the special function for getting 
		"""
		result = list.__getitem__(self,key)
		try:
			self.get_func(self,key)
		except AttributeError:
			pass

	def setter(self,fn):
		"""
		This is a decorator which sets the custom set function.
		"""

		self.set_func = fn
		return fn

	def __setitem__(self,key,value):
		list.__setitem__(self,key,value)
		try:
			self.set_func(self,key,value)
		except AttributeError:
			pass

	def append(self,value):
		CustomList.__setitem__(self,-1,value)

	def extend(self,iterable):
		for item in iterable:
			CustomList.append(item)

	def insert(self,position,value)
		list.insert(self,position,value)
		self.__setitem__(self,position,value)


	def deleter(self,fn):
		"""
		This decorator sets the custom del function.
		The function should take arg, (key)
		"""
		self.del_func = fn
		return fn

	def __delitem__(self,key):
		list.__delitem__(self,key)
		try:
			self.del_func(self,key)
		except AttributeError:
			pass


	def remove(self,value):
		del list.index(self,value)

	def pop(self,index=-1):
		result = self[index]
		del self[index]
		return result
