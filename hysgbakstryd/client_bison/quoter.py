#!/usr/bin/python
# 0.4.24
from cherrypy._cpconfig import _engine_namespace_handler
from urllib import urlopen
import json

class quoter(object):
	def __init__(self):
		self.printDebug = False

	def debug(self, txt):
		if self.printDebug:
			print txt

	def loadRandomQuotes(self):
		unwantedStarts = ['[[w:',"''[", '{{', '[http:', "''[[", '[[s:' ]
		unwantedContains = ['[[User:']
		toBeReplaced = ['[',']','{','}','|','w:',"'"]
		self.debug('T1')
		try:
			titlesXml = urlopen("http://en.wikiquote.org/w/api.php?action=query&list=random&rnnamespace=0&rnlimit=10&format=json&continue=").read()
			#http://en.wikiquote.org/w/api.php?action=query&list=random&rnnamespace=0&rnlimit=10&format=json&continue=
			jsonResults =json.loads(titlesXml)
			self.debug(jsonResults)
			titles = []
			for title in jsonResults[u'query'][u'random']:
				titles.append(title[u'title'])

			'''titlesSplit1 = titlesXml.split('title=&quot;')
			titles = []
			self.debug(titles)
			for title in titlesSplit1:
				if '&quot; /&gt;' in title:
					titles.append(title.split('&quot; /&gt;')[0])'''
			quotes = []
			for title in titles:
				self.debug('title:' + str(title))
				page = urlopen("http://en.wikiquote.org/w/api.php?action=query&prop=revisions&titles="+ title +"&rvprop=content&format=xml").read()
				self.debug(page)

				lines = page.split("\n")
				for line in lines:
					line = line.strip()
					if line.startswith('* ') and not line.startswith('**') and not (line.startswith('[') and line.endswith(']')):
						line = line.replace('* ', '')
						hasUnwantedFoo = False
						for uws in unwantedStarts:
							if line.startswith(uws):
								#print 'foo1:',uws
								hasUnwantedFoo = True
								break

						for uwc in unwantedContains:
							if uwc in line:
								#print 'foo2:',uwc
								hasUnwantedFoo = True
								break

						if hasUnwantedFoo == False:
							for tbr in toBeReplaced:
								line = line.replace(tbr, '')

							line = line.replace('&lt;br&gt;', '"')

							if '&quot;' in line:
								line = line.split('&quot;')[0]

							line = line.strip()
							if line != '' and len(line) >= 2 and len(line) < 256:
								quotes.append(line)
							else:
								pass
								#print 'len(line)', len(line)

			return quotes
		except Exception, e:
			print 'ERROR: in WIKI: ' + str(e)

		return []

if __name__ == "__main__":
	qt = quoter()
	for quote in qt.loadRandomQuotes():
		print("Quote: " + quote)