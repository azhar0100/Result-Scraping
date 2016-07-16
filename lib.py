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

	@_lazy_property.deleter
	def _lazy_deleter:
		delattr(self,attr_name)

	return _lazy_property

def throw_away_property(fn)
	"""This decorator should be applied before lazy_property"""
	prop = lazy_property(fn)
	if not hasattr(self,'global_deps')
		setattr(self,'global_deps',{})
	getattr(self,'global_deps').update({prop:[]})

	return prop

def depends(self,prop):
	"""This decorator should be applied before lazy_property"""
	def _decorated(fn,*args,**kwargs)
		result = fn(*args,**kwargs)
		self.global_deps.remove(prop)
		if not self.global_deps:
			del self.prop

	return _decorated
