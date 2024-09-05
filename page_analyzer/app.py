from urllib.parse import urlparse, urlunparse
from flask import Flask, render_template, redirect, url_for, flash, request, Response
from dotenv import load_dotenv
import os
from .tools import is_valid_url, dictionarize_soup_url
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
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def home() -> str:
    return render_template('index.html')

@app.route('/urls/<int:url_id>')
def specific_url(url_id: int) -> str | Response:
    url, checks = fetch_url_by_id(url_id)
    if not url:
        flash('URL not found', 'danger')
        return redirect(url_for('home'))
    return render_template('urls/index.html', url=url, checks=checks)

@app.route('/urls')
def list_urls() -> str:
    urls = fetch_all_urls()
    return render_template('urls/urls.html', urls=urls)

@app.route('/urls', methods=['POST'])
def add_new_url() -> Response:
    url = request.form['url']

    if not is_valid_url(url):
        flash('Invalid URL', 'danger')
        return redirect(url_for('home'))

    parsed_url = urlparse(url)
    normalized_url = urlunparse(
        (parsed_url.scheme, parsed_url.netloc, '', '', '', '')
    )

    connection = None
    try:
        connection = connect_to_db()
        existing_url = url_exists(normalized_url)

        if existing_url:
            flash('URL already exists', 'success')
            result = redirect(
                url_for('specific_url', url_id=existing_url['id'])
            )
        else:
            new_url_id = add_url(normalized_url)
            connection.commit()
            flash('Page successfully added', 'success')
            result = redirect(url_for('specific_url', url_id=new_url_id))
    except Exception as e:
        if connection:
            connection.rollback()
        flash(f"An error occurred: {str(e)}", 'danger')
        result = redirect(url_for('home'))
    finally:
        if connection:
            connection.close()

    return result

@app.route('/urls/<int:url_id>/check', methods=['POST'])
def add_check_url(url_id: int) -> Response:
    try:
        url_data = fetch_url_by_id(url_id)[0]
        url = url_data[1]
        dict_url_data = dictionarize_soup_url(url)
        add_url_to_check(dict_url_data, url_id)
        flash('URL successfully added to check', 'success')
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')

    return redirect(url_for('specific_url', url_id=url_id))

