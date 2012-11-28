from flask import Flask, render_template, request
from pymongo import Connection
import json
import os
import re

import reflection_scraper

app = Flask(__name__)
connection = Connection()
db = connection.reflections
collection = db.words

reflections_dict = {}

@app.route('/')
def start():
	return render_template('index.html')

#How do we return an icon???
@app.route('/favicon.ico')
def get_icon():
	return

@app.route('/<name>', methods=["GET"])
	#create match_data to return as json object for display

	#d3 template expects a dictionary with 2 key value pairs:
	#'name':name of node and 'children':list of child nodes 

	#child nodes are written as dictionaries identical to the one
	#described above.

def get_JSON(name):
	match_data = {}

	match_data['name'] = name
	match_data['children'] = []

	doc = collection.find_one({'name':name})
	my_keywords = doc['keywords'].keys()

	for keyword in my_keywords:
		word_data = {}
		word_data['name'] = keyword
		word_data['children'] = []

		match_names = []
		match_docs = collection.find({'keywords.'+keyword:{'$exists':True}}).sort('keywords.'+keyword, -1)
	
		for match_doc in match_docs[:10]:
			if match_doc['name'] != name:
				match_names.append(match_doc['name'])

		for person in match_names:
			# INCLUDE TO CONCEAL LAST NAMES
			# space1 = person.find(" ")
			# space2 = person.find(" ", space1+1)

			person_data = {}
			num_kw_matches = collection.find_one({'name':person})['keywords'][keyword]
			person_data['name'] = (person
			# INCLUDE TO CONCEAL LAST NAMES
			# [:space1] 
			+ " (" + str(num_kw_matches) + ")" )
			word_data['children'].append(person_data)

		match_data['children'].append(word_data)

	return json.dumps(match_data)

@app.route('/<name>/<term>')
def get_mentions(name, term):
	global reflections_dict
	if len(reflections_dict) == 0:
		reflections_dict = get_ref_dict(name, term)
	print reflections_dict
	places = [m.start() for m in re.finditer(term, reflections_dict[name])]
	snippets = []
	for loc in places:
		snippets.append(['...' + reflections_dict[name][loc-100:loc+100] + '...'])
	return json.dumps(snippets)

def get_ref_dict(name, term):
	return reflection_scraper.scrape_reflections(reflection_scraper.get_reflections(reflection_scraper.get_file_names('html/')))
	
if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5757))
	app.run(debug=True)


