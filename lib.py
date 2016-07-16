from itertools import islice

def split_every(n, iterable):
    i = iter(iterable)
    piece = list(islice(i, n))
    while piece:
        yield piece
        piece = list(islice(i, n))

def lazy_imap(func,arglist,pool,chunksize=1,ordered=True):
	for chunk in split_every(chunksize,arglist):
		if ordered:
			chunk_results = pool.imap(func,chunk)
		else:
			chunk_results = pool.imap_unordered(func,chunk)
		for chunk_result in chunk_results:
			yield chunk_result

def lazy_property(fn):
	attr_name = '__lazy__' + fn.__name__

	@property
	def _lazy_property(self):
		if not hasattr(self,attr_name):
			setattr(self,attr_name,fn(self))
		return getattr(self,attr_name)

	return _lazy_property

class ThrowAwayProperty(object):

	def __init__(self,fn):
		self.dependencies = []
		self.fn = lazy_property(fn)

	def __call__(self,*args,**kwargs):
		return self.fn(*args,**kwargs)

	def dependency(other_self,fn):
		other_self.dependencies.append[fn]
		return DependantProperty(fn,self)

class DependantProperty(object):

	def __init__(self,fn,prop):
		self.fn = fn
		self.prop = prop

	def __call__(self,*args,**kwargs):
		result = self.fn(*args,**kwargs)
		self.prop.dependencies.remove(value)
		return result
