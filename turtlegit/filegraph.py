from rdflib.graph import Graph
from rdflib.namespace import Namespace
from otsrdflib import OrderedTurtleSerializer
from urllib.parse import quote_plus, unquote_plus
import io
import logging as log
import posixpath
from os import path

class FileGraph:

	g = None
	repopath = None
	reponame = None
	domain = None
	filename = None
	filepath = None
	
	def __init__(self, iri, domain, repopath, reponame):
		self.iri = iri
		self.domain = domain
		self.repopath = repopath
		self.reponame = reponame
		self.g = Graph()
		
		log.info("IRI: "+self.iri)
		log.info("DOMAIN: "+domain)
		if iri.startswith(domain):
			self.filename = iri.rsplit('/', 1)[-1]
			if not self.filename.endswith('.ttl'):
				self.filename += '.ttl'
		else:
			self.filename = quote_plus(iri.replace(domain+self.reponame,''))+".ttl"
			
		self.filepath = posixpath.join(repopath,self.filename)

	def doExists(self):
		return path.isfile(self.filepath)

	def parseFile(self, f):
		self.g.parse(f, format='turtle')
		
	def parseString(self, modelString):
		f = io.StringIO(modelString)
		self.g.parse(f, format='turtle')
		
	def parsePath(self):
		self.g.parse(self.filepath, format='turtle')
		
	def serialize(self):
		serializer = OrderedTurtleSerializer(self.g)
		with open(self.filepath, 'wb') as fp:
			serializer.serialize(fp)