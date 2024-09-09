from os import getenv
from typing import Tuple
from urllib.parse import urlparse, urlunparse
from dotenv import load_dotenv
from validators import url as url_validator
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    Response
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
    return render_template('index.html')


@app.route('/urls/<int:url_id>')
def specific_url(url_id: int) -> str | Response:
    connection = connect_to_db()
    url, checks = fetch_url_by_id(url_id, connection)
    if not url:
        flash('Сайт не найден', 'danger')
        return redirect(url_for('home'))
    return render_template('urls/index.html', url=url, checks=checks)


@app.route('/urls')
def list_urls() -> str:
    connection = connect_to_db()
    urls = fetch_all_urls(connection)
    return render_template('urls/urls.html', urls=urls)


@app.route('/urls', methods=['POST'])
def add_new_url() -> Response | Tuple[str, int]:
    url = request.form['url']

    if not url_validator(url) and not len(url) >= 255:
        flash('Некорректный URL', 'danger')
        return render_template('index.html'), 422

    normalized_url = urlunparse(urlparse(url)[:2] + ('', '', '', ''))

    connection = None
    try:
        connection = connect_to_db()
        existing_url = url_exists(normalized_url, connection)

        if existing_url:
            flash('Страница уже существует', 'success')
            return redirect(
                url_for('specific_url', url_id=existing_url['id'])
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
    connection = None
    try:
        connection = connect_to_db()
        url_data = fetch_url_by_id(url_id, connection)[0]
        url = url_data[1]
        dict_url_data = dictionarize_soup_url(url)
        add_url_to_check(dict_url_data, url_id, connection)
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
