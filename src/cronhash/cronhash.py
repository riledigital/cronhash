#from bs4 import BeautifulSoup
import requests
import sqlite3
import hashlib
from datetime.datetime import datetime
import pickle

def initialize_database(file_db):
	con = sqlite3.connect('data.db')
	cur = con.cursor()
	# Create table if not exists
	cur.execute('''CREATE TABLE IF NOT EXISTS sites
				(
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		url TEXT NOT NULL,
		previous_update TEXT,
		last_updated TEXT,
		hash TEXT,
		content BLOB
	)
	''')
	return cur

def fetch_url_data(url):
	response = requests.get(url)
	hashed = hashlib.sha256()
	hashed.update(response.text)
	hash_str = hashed.digest()

	last_updated = datetime.now().isoformat()
	# last_updated = datetime.now().fromisoformat()

	content = pickle.dumps(response)
	return (None, url, last_updated, hash_str, content)

if __init__ == '__main__':
	tup = fetch_url_data('http://example.org')
	print(tup)