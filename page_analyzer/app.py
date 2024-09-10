from os import getenv
from typing import Tuple
from urllib.parse import urlparse, urlunparse, ParseResult
from dotenv import load_dotenv
from validators import url as url_validator
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
from .tools import dictionarize_soup_url
from .db import (
    connect_to_db,
    add_url,
    fetch_all_urls,
    fetch_url_by_id,
    url_exists,
    add_url_to_check
)


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = getenv('SECRET_KEY')


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

    connection = connect_to_db()
    url, checks = fetch_url_by_id(url_id, connection)
    if not url:
        abort(404, description="Сайт не найден")
    return render_template('urls/index.html', url=url, checks=checks)


@app.route('/urls')
def list_urls() -> str:
    """
    Displays a list of all URLs and their checks.

    Returns:
        str: The rendered HTML content listing all URLs.
    """

    connection = connect_to_db()
    urls = fetch_all_urls(connection)
    return render_template('urls/urls.html', urls=urls)


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

    url = request.form['url']

    if not url_validator(url) or len(url) >= 255:
        flash('Некорректный URL', 'danger')
        return render_template('index.html'), 422

    parsed_url = urlparse(url)
    normalized_url = urlunparse(ParseResult(scheme=parsed_url.scheme,
                                            netloc=parsed_url.netloc,
                                            path='',
                                            params='',
                                            query='',
                                            fragment=''))

    connection = None
    try:
        connection = connect_to_db()
        existing_url = url_exists(normalized_url, connection)

        if existing_url:
            flash('Страница уже существует', 'success')
            existing_url_id = existing_url.get('id')
            return redirect(
                url_for('specific_url', url_id=existing_url_id)
            )
        else:
            new_url_id = add_url(normalized_url, connection)
            connection.commit()
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('specific_url', url_id=new_url_id))

    except Exception:
        if connection:
            connection.rollback()
        flash("An error occurred", 'danger')
        return redirect(url_for('home'))

    finally:
        if connection:
            connection.close()


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

    connection = None
    try:
        connection = connect_to_db()
        url_data, _ = fetch_url_by_id(url_id, connection)
        url = url_data.get('name')
        soup_url_data = dictionarize_soup_url(url)
        add_url_to_check(soup_url_data, url_id, connection)
        connection.commit()
        flash('Страница успешно проверена', 'success')
    except Exception:
        if connection:
            connection.rollback()
        flash("Произошла ошибка при проверке", 'danger')
    finally:
        if connection:
            connection.close()

    return redirect(url_for('specific_url', url_id=url_id))
