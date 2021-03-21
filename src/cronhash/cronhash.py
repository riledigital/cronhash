#from bs4 import BeautifulSoup
import requests
import sqlite3
import hashlib
from datetime import datetime
import pickle
from uuid import uuid4

def initialize_database(file_db = 'data.db'):
	con = sqlite3.connect(file_db)
	cur = con.cursor()
	# Create table if not exists
	cur.execute('''CREATE TABLE IF NOT EXISTS sites
				(
		id TEXT PRIMARY KEY,
		url TEXT NOT NULL,
		previous_updated TEXT,
		previous_hash TEXT,
		newest_updated TEXT,
		newest_hash TEXT,
		content BLOB
	)
	''')
	return (con, cur)

def fetch_url_data(url):
	response = requests.get(url)
	hashed = hashlib.sha256()
	hashed.update(response.text.encode('utf-8'))
	hash_str = hashed.hexdigest()

	last_updated = datetime.now().isoformat()
	# last_updated = datetime.now().fromisoformat()

	content = pickle.dumps(response)
	return (str(uuid4()), url, None, None, last_updated, hash_str, content)

def site_record_exists(con, cur, url):
	cur.execute("SELECT id,url from sites WHERE url=?", (url,))
	existing = cur.fetchone()
	return existing is not None

def add_new_site(con, cur, url):
	if site_record_exists(con, cur, url):
		print(f"Skipping insert, site already exists: {url}")
	else:
		insert_update_record(con, cur, (str(uuid4()), url, None, None, None, None, None))

def insert_update_record(con, cur, record):
	# Lookup existing record
	cur.execute("SELECT id,url from sites WHERE url=?", (record[1],))
	existing = cur.fetchone()
	if (existing):
		print(f"Found existing url!! {existing}")
		cur.execute("""
		UPDATE sites
			SET
				previous_updated = newest_updated,
				previous_hash = newest_hash,
				newest_updated = ?,
				newest_hash = ?
			WHERE
				url = ?
		""", (record[4], record[5], record[1]))
	else: # If it exists, move latest to prev, and set new dates/hashes
		cur.execute('INSERT INTO sites VALUES (?,?,?,?,?,?,?)', record)
	con.commit()

def list_changed_records(con, cur):
	records = cur.execute("SELECT * from sites WHERE previous_hash != newest_hash").fetchall()
	return records

def fetch_update_url(con, cur, url):
	"""Composite operation

	Args:
		con ([type]): [description]
		cur ([type]): [description]
		url ([type]): [description]
	"""
	tup = fetch_url_data('http://example.org')
	insert_update_record(con, cur, tup)
	print(list_changed_records(con, cur))

def get_all_records(con, cur):
	cur.execute("""SELECT url from sites""")
	records = cur.fetchall()
	return records

def scan_all(con, cur, records):
	for site in records:
		new_record = fetch_url_data(site[0])
		insert_update_record(con, cur, new_record)

if __name__ == '__main__':
	con, cur = initialize_database('data.db')
	add_new_site(con, cur, "https://google.com")
	# fetch_update_url(con, cur, 'http://example.org')
	scan_all(con, cur, get_all_records(con, cur))