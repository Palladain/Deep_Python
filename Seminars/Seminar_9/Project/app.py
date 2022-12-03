import sqlite3
import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# конфигурация

DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    """Соединяет с указанной базой данных."""
    rv = sqlite3.connect(app.config['DATABASE']) # внутри конфигураций надо будет указать БД, в которую мы будем все хранить
    rv.row_factory = sqlite3.Row #инстанс для итерации по строчкам (может брать по строке и выдавать)
    return rv

def get_db():
    """Если ещё нет соединения с базой данных, открыть новое - для текущего контекста приложения"""
    if not hasattr(g, 'sqlite_db'): #g - это наша глобальная переменная, являющасяс объектом отрисовки
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext #декоратор при разрыве connection
def close_db(error): #закрытие может проходить как нормально, так и с ошибкой, которую можно обрабатывать
    """Закрываем БД при разрыве"""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    """Инициализируем наше БД"""
    with app.app_context(): # внутри app_context app и g связаны
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/')
def hello_page():
    return render_template("layout.html")

@app.route('/posts')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)', [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out, wow')
    return redirect(url_for('hello_page'))


if __name__ == '__main__':
    init_db()
    app.run()
