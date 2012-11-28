import request 
import reflection_scraper 
import db
import json

request.download_reflections_pages()
master_list = reflection_scraper.get_peoples_words()
f = open('master_list.js', 'w')
s = json.dumps(master_list, f)
f.write('var master_list='+s)
f.close()
db.save_words_in_reflections(master_list)