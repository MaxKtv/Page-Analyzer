from urllib import request
from urllib.parse import urlparse, urlunparse
from flask import Flask, render_template, redirect, url_for, flash
from dotenv import load_dotenv
import os
from .validator import is_valid_url
from .db import CONN, add_url_to_db, get_all_urls

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/urls/<int: id>')
def get_url_(id):
    if is_valid_url(id):
        return render_template('new.html', id=id)
    else:
        pass

@app.route('/urls')
def get_urls():
    urls = get_all_urls()
    return render_template('urls/index.html', urls=urls)

@app.route('/urls', methods=['POST'])
def add_url():
    url = request.form['url']
    if is_valid_url(url):
        parsed_url = urlparse(url)
        normalized_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))
        url_id = add_url_to_db(normalized_url)
        CONN.commit()
        flash(f'Page successfully added', 'alert-success')
        return redirect(url_for('get_url_', id=url_id))
    else:
        return render_template('index.html', error='Invalid URL'), 400
