class CustomList(list):
"""
This class is basically a superclass which makes it possible to implement extra operations
during list get ,set and delete by subclassing it and implementing custom magic methods.
"""
	def append(self,value):
		CustomList.__setitem__(self,-1,value)

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
