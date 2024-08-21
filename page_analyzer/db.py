from datetime import datetime
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
CONN = psycopg2.connect(DATABASE_URL)
CURS = CONN.cursor()

def add_url_to_db(url):
    CURS.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id;', (url, datetime.now()))
    return CURS.fetchone()['id']

def get_all_urls():
    CURS.execute('SELECT * FROM urls ORDER BY created_at DESC;')
    return CURS.fetchall()