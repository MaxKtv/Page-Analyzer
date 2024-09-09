from datetime import datetime
import os
from typing import Tuple

from dotenv import load_dotenv
from psycopg2 import extras, connect

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


def connect_to_db():
    try:
        return connect(DATABASE_URL, cursor_factory=extras.DictCursor)
    except Exception as e:
        raise f'Could not connect to database: {e}'


def add_url(url, conn):
    with conn.cursor() as curs:
        curs.execute(
            'INSERT INTO urls (name, created_at) '
            'VALUES (%s, %s) RETURNING id;',
            (url, datetime.now())
        )
        url_id = curs.fetchone()['id']
    return url_id


def fetch_all_urls(conn):
    with conn.cursor() as curs:
        curs.execute(
            'SELECT urls.id, urls.name, url_checks.created_at, '
            'url_checks.status_code '
            'FROM urls '
            'LEFT JOIN url_checks ON urls.id = url_checks.url_id '
            'ORDER BY urls.created_at DESC;'
        )
        urls = curs.fetchall()
    return urls


def fetch_url_name_by_id(url_id, conn):
    with conn.cursor() as curs:
        curs.execute(
            'SELECT name FROM urls WHERE id = %s;',
            (url_id,))
        result = curs.fetchone()
    return result['name'] if result else None


def fetch_url_by_id(url_id, conn) -> Tuple:
    with conn.cursor() as curs:
        curs.execute('SELECT * FROM urls WHERE id = %s;', (url_id,))
        url_data = curs.fetchone()
        curs.execute('SELECT * FROM url_checks WHERE url_id = %s '
                     'ORDER BY created_at DESC;', (url_id,))
        checks = curs.fetchall()
    return url_data, checks


def url_exists(url, conn) -> Tuple | None:
    with conn.cursor() as curs:
        curs.execute('SELECT * FROM urls WHERE name = %s;', (url,))
        result = curs.fetchone()
    return result


def add_url_to_check(data, url_id, conn):
    with conn.cursor() as curs:
        curs.execute(
            'INSERT INTO url_checks '
            '(url_id, status_code, h1, title, description, created_at) '
            'VALUES (%s, %s, %s, %s, %s, %s);',
            (url_id, data['status_code'], data['h1'],
             data['title'], data['description'], datetime.now())
        )
