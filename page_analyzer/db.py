from datetime import datetime
import os
from typing import Tuple, List, Dict, Any
from dotenv import load_dotenv
from psycopg2 import extras, connect
from psycopg2.extensions import connection


load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


def connect_to_db() -> connection:
    """
    Establishes a connection to the database.

    Loads environment variables from the `.env` file,
    retrieves the database URL,
    and creates a connection to the database using psycopg2.

    Returns:
        connection (connection): The database connection.

    Raises:
        ConnectionError: If the database connection cannot be established.
    """

    try:
        return connect(DATABASE_URL, cursor_factory=extras.DictCursor)
    except Exception as e:
        raise ConnectionError(f'Could not connect to database: {e}')


def add_url(url: str, conn: connection) -> int:
    """
    Adds a new URL to the `urls` table.

    Args:
        url (str): The URL to be saved in the database.
        conn (connection): Active database connection.

    Returns:
        int: The ID of the newly added URL.

    Raises:
        Exception: If an error occurs during the SQL execution.
    """

    with conn.cursor() as curs:
        curs.execute(
            'INSERT INTO urls (name, created_at) '
            'VALUES (%s, %s) RETURNING id;',
            (url, datetime.now())
        )
        result = curs.fetchone()
    return result.get('id')


def fetch_all_urls(conn: connection) -> List[Tuple[Any, ...]]:
    """
    Retrieves a list of all URLs from the database
    with associated check information.

    Args:
        conn (connection): Active database connection.

    Returns:
        List[Tuple[Any, ...]]: A list of URLs and their checks,
        ordered by creation date.
    """

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


def fetch_url_name_by_id(url_id: int, conn: connection) -> str | None:
    """
    Fetches the name (URL) by its ID.

    Args:
        url_id (int): The ID of the URL in the database.
        conn (connection): Active database connection.

    Returns:
        str: The URL if found, None otherwise.
    """

    with conn.cursor() as curs:
        curs.execute(
            'SELECT name FROM urls WHERE id = %s;',
            (url_id,))
        result = curs.fetchone()
    return result.get('name')


def fetch_url_by_id(url_id: int, conn: connection) \
        -> Tuple[Dict[str, Any], List]:
    """
    Retrieves data about the URL and its checks by URL ID.

    Args:
        url_id (int): The ID of the URL in the database.
        conn (connection): Active database connection.

    Returns:
        Tuple[Dict[str, Any], List]: A tuple containing the URL data
        and a list of checks.
    """

    with conn.cursor() as curs:
        curs.execute('SELECT * FROM urls WHERE id = %s;', (url_id,))
        url_data = curs.fetchone()
        id, name, created_at = url_data
        url_dicted_data = {
            'id': id,
            'name': name,
            'created_at': created_at
        }

        curs.execute('SELECT * FROM url_checks WHERE url_id = %s '
                     'ORDER BY created_at DESC;', (url_id,))
        checks = curs.fetchall()

    return url_dicted_data, checks


def url_exists(url: str, conn: connection) -> Tuple | None:
    """
    Checks if a URL already exists in the database.

    Args:
        url (str): The URL to check.
        conn (connection): Active database connection.

    Returns:
        tuple | None: A dict with URL data if it exists, None otherwise.
    """

    with conn.cursor() as curs:
        curs.execute('SELECT * FROM urls WHERE name = %s;', (url,))
        result = curs.fetchone()
    return result


def add_url_to_check(data: Dict[str, Any], url_id: int, conn) -> None:
    """
    Adds a URL check entry to the `url_checks` table.

    Args:
        data (Dict[str, Any]): A dictionary containing data
        status code, h1, title, description.
        url_id (int): The ID of the URL being checked.
        conn (connection): Active database connection.

    Returns:
        None
    """

    with conn.cursor() as curs:
        curs.execute(
            'INSERT INTO url_checks '
            '(url_id, status_code, h1, title, description, created_at) '
            'VALUES (%s, %s, %s, %s, %s, %s);',
            (
                url_id,
                data.get('status_code'),
                data.get('h1'),
                data.get('title'),
                data.get('description'),
                datetime.now()
            )
        )
