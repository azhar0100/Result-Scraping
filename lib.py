from itertools import islice
import logging

logger = logging.getLogger(__name__)
logger.setLevel(8)
file_handler = logging.FileHandler("lib.log")
file_handler.setLevel(8)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

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

def lazy_prop_func(fn):
	logger.info("lazy_prop_func called on {}".format(fn))
	attr_name = '__lazy__' + fn.__name__

	def _lazy_property(self):
		if not hasattr(self,attr_name):
			setattr(self,attr_name,fn(self))
		return getattr(self,attr_name)

	return _lazy_property
def lazy_property(fn):
	attr_name = '__lazy__' + fn.__name__

	@property
	def _lazy_property(self):
		if not hasattr(self,attr_name):
			setattr(self,attr_name,fn(self))
		return getattr(self,attr_name)

	# @_lazy_property.deleter
	# def _lazy_deleter(self):
	# 	delattr(self,attr_name)

	return _lazy_property

def throw_away_property(fn):
	"""This decorator should be applied after lazy_property"""
	prop = lazy_property(fn)
	@property
	def _throw_away_property(self):
		if not hasattr(self,'global_deps'):
			self.global_deps = {}
		self.global_deps.update({prop:[]})
		return prop.fget(self)

	return _throw_away_property

class LazyProperty(object):

	def __init__(self,fn):
		self.fn = fn

	def __get__(self,instance):
		if not hasattr(self,'data'):
			self.data = self.fn(instance)
		return self.data

	def __delete__(self,instance):
		del self.data

class ThrowAwayProperty(LazyProperty):
	"""This property has dependencies ,it is thrown away when they are fulfilled"""
	def __init__(self,fn):
		self.dependencies = []

	def dependency(self,fn):
		"""Decorator to bind dependencies."""
		DependantProperty(fn,self)


class DependantProperty(LazyProperty):

	def __init__(self,fn,prop):
		"""prop is the ThrowAwayProperty on which this property depends"""
		LazyProperty.__init__(self,fn)
		self.fn = fn
		self.prop = prop
		prop.dependencies.append(self)

	def __get__(self,instance):
		result = self.fn(instance)
		self.prop.dependencies.remove(self)
		# Though simple , should be replaced by logic in a special dependencies descriptor
		if not self.prop.dependencies:
			self.prop.__delete__(instance)
		return result

def depends(prop):
	"""This decorator should be applied before lazy_property"""
	logger.info("depends called with {}".format(prop))
	
	def _depends(fn,*args,**kwargs):
		logger.info("_depends called with {},{},{}".format(fn,args,kwargs))
		@property		
		def _prop(self,*args,**kwargs):
			logger.info("Called with fn {}".format(fn))
			result = fn(self,*args,**kwargs)
			del self.global_deps[prop]
			if not self.global_deps:
				del self.prop
			return result
		self.global_deps[prop].append(_prop)
		return _prop
	return _depends
