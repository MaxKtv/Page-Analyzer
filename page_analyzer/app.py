from urllib.parse import urlparse, urlunparse
from flask import Flask, render_template, redirect, url_for, flash, request
from dotenv import load_dotenv
import os
from .validator import is_valid_url
from .db import connect_to_db, add_url, fetch_all_urls, fetch_url_by_id, url_exists

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/urls/<int:id>')
def specific_url(id: int):
    url = fetch_url_by_id(id)
    if not url:
        flash('URL not found', 'danger')
        return redirect(url_for('home'))
    return render_template('urls/index.html', url=url)

@app.route('/urls')
def list_urls():
    urls = fetch_all_urls()
    return render_template('urls/urls.html', urls=urls)

@app.route('/urls', methods=['POST'])
def add_new_url():
    url = request.form['url']

    if not is_valid_url(url):
        flash('Invalid URL', 'danger')
        return redirect(url_for('home'))

    parsed_url = urlparse(url)
    normalized_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))

    connection = None
    try:
        connection = connect_to_db()
        existing_url = url_exists(normalized_url)

        if existing_url:
            flash('URL already exists', 'success')
            result = redirect(url_for('specific_url', id=existing_url['id']))
        else:
            url_id = add_url(normalized_url)
            connection.commit()
            flash('Page successfully added', 'success')
            result = redirect(url_for('specific_url', id=url_id))
    except Exception as e:
        if connection:
            connection.rollback()
        flash(f"An error occurred: {str(e)}", 'danger')
        result = redirect(url_for('home'))
    finally:
        if connection:
            connection.close()

    return result

