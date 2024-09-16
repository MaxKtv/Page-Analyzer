from datetime import datetime
from typing import Tuple, List, Dict, Any
from dotenv import load_dotenv
from psycopg2 import extras, connect, OperationalError, DatabaseError
from psycopg2.extensions import connection
from psycopg2.extras import DictRow

load_dotenv()


def connect_to_db(conn: str | None) -> connection:
    """
    Establishes a connection to the database.

    Loads environment variables from the `.env` file,
    retrieves the database URL,
    and creates a connection to the database using psycopg2.

    Args:
        conn (str | None): The database URL.

    Returns:
        connection (connection): The database connection.

    Raises:
        ConnectionError: If the database connection cannot be established.
    """

    try:
        return connect(conn, cursor_factory=extras.DictCursor)
    except (DatabaseError, OperationalError) as e:
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


def fetch_all_urls(conn: connection) -> List[Dict[str, Any]]:
    """
    Retrieves a list of all URLs from the database
    along with the latest check information.

    Args:
        conn (connection): Active database connection.

    Returns:
        List[Dict[str, Any]]: A list of URLs and their most recent checks,
        ordered by creation date.
    """

    with conn.cursor() as curs:
        curs.execute(
            'SELECT id, name FROM urls ORDER BY id DESC;'
        )
        urls = curs.fetchall()

    result = []
    for url in urls:
        url_id = url['id']
        name = url['name']

        with conn.cursor() as curs:
            curs.execute(
                'SELECT created_at, status_code '
                'FROM url_checks '
                'WHERE url_id = %s '
                'ORDER BY created_at DESC '
                'LIMIT 1;',
                (url_id,)
            )

            last_check = curs.fetchone()

            result.append({
                'id': url_id,
                'name': name,
                'last_check': last_check['created_at'] if last_check else None,
                'status_code': last_check['status_code'] if last_check else None
            })

    return result


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
        data = curs.fetchone()
        url_name = data.get('name')
    return url_name


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

        url_id, name, created_at = url_data
        url_dicted_data = {
            'id': url_id,
            'name': name,
            'created_at': created_at
        }

        curs.execute('SELECT * FROM url_checks WHERE url_id = %s '
                     'ORDER BY created_at DESC;', (url_id,))
        checks = curs.fetchall()

    return url_dicted_data, checks


def url_exists(url: str, conn: connection) -> DictRow | None:
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
    data_insert_field = data.keys()
    data_insert_values = data.values()

    insert_field = f"url_id, {', '.join(data_insert_field)}, created_at"
    insert_values = url_id, *data_insert_values, datetime.now()
    field_values = ', '.join(['%s'] * len(insert_values))

    with conn.cursor() as curs:
        curs.execute(f"INSERT INTO url_checks ({insert_field}) "
                     f"VALUES ({field_values});", insert_values)
