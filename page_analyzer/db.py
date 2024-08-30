from datetime import datetime
import os
from dotenv import load_dotenv
from psycopg2 import extras, connect

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def connect_to_db():
    return connect(DATABASE_URL, cursor_factory=extras.DictCursor)

def add_url(url):
    with connect_to_db() as conn:
        with conn.cursor() as curs:
            curs.execute(
                'INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id;',
                (url, datetime.now())
            )
            url_id = curs.fetchone()['id']
        conn.commit()
    return url_id

def fetch_all_urls():
    with connect_to_db() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM urls ORDER BY created_at DESC;')
            urls = curs.fetchall()
    return urls

def fetch_url_name_by_id(url_id):
    with connect_to_db() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT name FROM urls WHERE id = %s;', (url_id,))
            result = curs.fetchone()
    return result['name'] if result else None

def fetch_url_by_id(url_id):
    with connect_to_db() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM urls WHERE id = %s;', (url_id,))
            url_data = curs.fetchone()
    return url_data

def url_exists(url):
    with connect_to_db() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM urls WHERE name = %s;', (url,))
            result = curs.fetchone()
    return result