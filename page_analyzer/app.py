from os import getenv
from typing import Tuple
from dotenv import load_dotenv
from requests import get as get_request
from requests.exceptions import RequestException
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    Response,
    abort
)
from .db import (
    connect_to_db,
    add_url,
    fetch_all_urls,
    fetch_url_by_id,
    url_exists,
    add_url_to_check
)
from .tools import dictionarize_soup_url, is_valid_url, normalize_url


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')
DATABASE_URL = getenv('DATABASE_URL')


@app.route('/')
def home() -> str:
    """
    Renders the homepage.

    Returns:
        str: The rendered HTML content for the homepage.
    """
    return render_template('index.html')


@app.route('/urls/<int:url_id>')
def specific_url(url_id: int) -> str | Response:
    """
    Displays a specific URL by its ID, along with its checks.

    Args:
        url_id (int): The ID of the URL to display.

    Returns:
        str: The rendered HTML content for the URL page.
        Response: Redirects to the homepage with
        a flash message if the URL is not found.
    """

    connection = connect_to_db(DATABASE_URL)

    try:
        url, checks = fetch_url_by_id(url_id, connection)

        if not url:
            abort(404, description="Сайт не найден")

        result = render_template('urls/index.html', url=url, checks=checks)

    except (ConnectionError, KeyError):
        flash('Internal Server Error', 'danger')
        result = render_template('index.html'), 500

    finally:
        connection.close()

    return result


@app.route('/urls')
def list_urls() -> str:
    """
    Displays a list of all URLs and their checks.

    Returns:
        str: The rendered HTML content listing all URLs.
    """

    connection = connect_to_db(DATABASE_URL)

    try:
        urls = fetch_all_urls(connection)
        result = render_template('urls/urls.html', urls=urls)

    except (ConnectionError, KeyError):
        flash('Internal Server Error', 'danger')
        result = render_template('index.html'), 500

    finally:
        connection.close()

    return result


@app.route('/urls', methods=['POST'])
def add_new_url() -> Response | Tuple[str, int]:
    """
    Adds a new URL to the database via a form submission.
    Validates the URL format, checks if it already exists, and adds it if not.

    Returns:
        Response: A redirect to the URL page if the URL is successfully added.
        Tuple[str, int]: Renders the homepage with
        a 422 status if the URL is invalid.
    """

    url = request.form.get('url')

    if not is_valid_url(url):
        flash('Некорректный URL', 'danger')
        return render_template('index.html'), 422

    normalized_url = normalize_url(url)
    connection = connect_to_db(DATABASE_URL)

    try:
        existing_url = url_exists(normalized_url, connection)

        if existing_url:
            flash('Страница уже существует', 'success')
            existing_url_id = existing_url.get('id')

            result = redirect(
                url_for('specific_url', url_id=existing_url_id)
            )

        else:
            new_url_id = add_url(normalized_url, connection)
            connection.commit()
            flash('Страница успешно добавлена', 'success')

            result = redirect(url_for('specific_url', url_id=new_url_id))

    except (ConnectionError, KeyError):
        flash('Internal Server Error', 'danger')
        result = render_template('index.html'), 500

    finally:
        connection.close()

    return result


@app.route('/urls/<int:url_id>/check', methods=['POST'])
def add_check_url(url_id: int) -> Response:
    """
    Adds a new check for the specified URL.

    Fetches the URL data, extracts relevant information,
    and inserts a new check record.

    Args:
        url_id (int): The ID of the URL being checked.

    Returns:
        Response: A redirect to the URL page
        after the check is successfully added.
    """

    connection = connect_to_db(DATABASE_URL)
    try:
        url_data, _ = fetch_url_by_id(url_id, connection)
        url = url_data.get('name')

        req = get_request(url, timeout=10)
        req.raise_for_status()
        soup_url_data = dictionarize_soup_url(req)

        add_url_to_check(soup_url_data, url_id, connection)
        connection.commit()
        flash('Страница успешно проверена', 'success')

    except (ConnectionError, KeyError):
        connection.rollback()
        flash('Internal Server Error', 'danger')

    except RequestException:
        connection.rollback()
        flash('Произошла ошибка при проверке', 'danger')

    except ValueError as e:
        connection.rollback()
        flash(f'Something went wrong: {e}', 'danger')

    finally:
        connection.close()

    return redirect(url_for('specific_url', url_id=url_id))
