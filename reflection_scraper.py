from bs4 import BeautifulSoup
import os
import re
import string

#create_frequency_dict can't handle keywords with characters like
#+, *, or ? that have special meanings in regex

def get_keywords(filename):
  '''input: path to text file passed as string
  output: list of lines in file with right newlines stripped'''
  keywords = []
  f = open(filename, 'r')
  for line in f:
    keywords.append(line.strip())
  return keywords

extra_stops = ['code', 'planned', 'learn', 'learned', 'learning', 'will', 'continue', 'time', "i'm", 'today', 'tomorrow', 'yesterday']

def generate_popular(reflections_mapping, extra_stops):
  '''input: mapping of names to reflections text
  output: list of top 50 popular 'key' words'''
  word_bucket = {}
  file = open('stopword.txt', 'r')
  dump = file.read()
  file.close()
  stopwords = dump.split()
  for person in reflections_mapping:
    words = reflections_mapping[person].strip().lower().split()
    for word in words:
      wordy = word.strip(string.punctuation+string.whitespace)
      if stopwords.count(wordy) == 0:
        if wordy in word_bucket:
          word_bucket[wordy] += 1
        else:
          word_bucket[wordy] = 1
  sorted = word_bucket.items()
  sorted.sort(key=lambda x: x[1])
  sorted.reverse()
  return sorted[0:50]

def get_file_names(dir_path):
  '''input: path to directory
  output: list of file names in directory'''
  files = os.listdir(dir_path)
  for index, file_name in enumerate(files):
    files[index] = dir_path + file_name
  return files

def get_reflections(file_names):
  '''input: list of file_names for downloaded HS site source 
  output: list reflections-for-day elements from HS site'''
  reflections = []
  for file in file_names:
    doc = BeautifulSoup(open(file))
    reflections += doc.select('.reflections-for-day > li')
  return reflections

def scrape_reflections(reflections):
  '''input: list of reflections-for-day elements from HS site
  output: dict mapping name: string of concatenated reflections text'''
  reflections_dict = {}
  for reflection in reflections:
    name = reflection.a.string[:-1]
    for p in reflection('p'):
      reflections_dict[name] = reflections_dict.get(name, "") + str(p.string).lstrip().lower()
  return reflections_dict 

def create_frequency_dict(keywords, reflection_str):
  '''input: list of keywords, string to search for keywords
  output: dict of keyword:num. instances in string if num>0'''
  frequency_dict = {}
  for keyword in keywords:
    re_keyword = re.compile('(?:\A|\W)' + re.escape(keyword) + '(?:\W|\Z)', re.IGNORECASE)
    count = len(re_keyword.findall(reflection_str))
    if count > 0:
      frequency_dict[keyword] = count
  return frequency_dict

def create_db_entry (keywords, name, reflection_str):
  '''input: list of keywords, name, string of reflections for name
  output: db entry {'name':name 'keywords':{kw1:freq, kw2:freq ...}}'''
  db_entry = {}
  db_entry['name'] = name
  frequency_dict = create_frequency_dict(keywords, reflection_str)
  db_entry['keywords'] = frequency_dict
  return db_entry

def create_db_entries(keywords, reflections_dict):
  '''input: list of keywords, dict of names:reflections strings
  output: list of db_entries to dump'''
  db_entries = []
  for name, reflection_str in reflections_dict.iteritems():
    db_entry = create_db_entry(keywords, name, reflection_str)
    db_entries.append(db_entry)
  return db_entries

KEYWORDS_FILENAME = "keywords.txt"
def get_peoples_words():
  keywords = get_keywords(KEYWORDS_FILENAME)
  file_names = get_file_names('html/')
  reflections = get_reflections(file_names)
  reflections_dict = scrape_reflections(reflections)
  db_entries = create_db_entries(keywords, reflections_dict)
  return db_entries