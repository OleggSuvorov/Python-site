# -*- coding:utf-8 -*-
from flask import Flask, request, render_template, redirect, url_for, session
from models.executeSqlite3 import executeSelectOne, executeSelectAll, executeSQL
from functools import wraps
from models.user_manager import UserManager
from models.user_type_manager import UserTypeManager
from models.base_manager import SNBaseManager
import os

# створюємо головний об'єкт сайту класу Flask
from models.post_manager import PostManager

app = Flask(__name__)
# добавляємо секретний ключ для сайту щоб шифрувати дані сессії
# при кожнаму сапуску фласку буде генечитись новий рандомний ключ з 24 символів
app.secret_key = os.urandom(24)
# app.secret_key = '125'


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'username' in session:
            if UserManager.load_models.get(session['username'], None):
                return f(*args, **kwargs)
        return redirect(url_for('login'))
    return wrap


# описуємо логін роут
# вказуємо що доступні методи "GET" і "POST"
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        # якщо метод пост дістаємо дані з форми і звіряємо чи є такий користвач в базі данних
        # якшо є то в дану сесію добавляєм ключ username
        # і перекидаємо користувача на домашню сторінку
        user = UserManager()
        if user.loginUser(request.form):
            addToSession(user)
            return redirect(url_for('home'))

    return render_template('index.html')



# описуємо роут для вилогінення
# сіда зможуть попадати тільки GET запроси
@app.route('/logout')
@login_required
def logout():
    user = session.get('username', None)
    if user:
        # якщо в сесії є username тоді видаляємо його
        del session['username']
    return redirect(url_for('login'))

@app.route('/add_friend', methods=['GET'])
@login_required
def add_friend():
    user_id = int(request.args.get('id',0))
    user = UserManager.load_models[session['username']]
    user.add_friend(id=user_id)
    return redirect(request.referrer)

@app.route('/user/<nickname>')
@login_required
def user_page(nickname):
    context = {}
    if session.get('username', None):
        user = UserManager.load_models[session['username']]
        context['loginUser'] = user

    selectUser = UserManager()
    selectUser.select().And([('nickname','=',nickname)]).run()
    context['user'] = selectUser

    return render_template('friend.html', context=context)

# описуємо домашній роут
# сіда зможуть попадати тільки GET запроси
@app.route('/')
@login_required
def home():
    context = {}
    if session.get('username', None):
        user = UserManager.load_models[session['username']]
        # якщо в сесії є username тоді дістаємо його дані
        # добавляємо їх в словник для передачі в html форму
        context['user'] = user
        context['loginUser'] = user
    return render_template('home.html', context=context)


def addToSession(user):
    session['username'] = user.object.nickname


@app.route('/registration', methods=["GET", "POST"])
def registr():
    context = {'Error': []}
    user_type = UserTypeManager()
    user_type.getTypeUser()
    if session.get('username', None):
        user = UserManager.load_models[session['username']]
        user_type.getTypeGroup()
        context['user'] = user
    context['type'] = user_type

    if request.method == 'POST':
        user = UserManager().getModelFromForm(request.form)
        if user.check_user():
            context['Error'].append('wrong name or email')
        if user.object.type.type_name == 'user':
            if not user.object.password :
                context['Error'].append('incorrect password')
        if context['Error']:
            return render_template('registration.html', context=context)
        if user.save():
            UserManager.load_models[user.object.nickname] = user
            addToSession(user)
            return redirect(url_for('home'))
        context['Error'].append('incorrect data')
    return render_template('registration.html', context=context)

@app.route('/add_post', methods=['GET','POST'])
@login_required
def add_post():
    if request.method == 'POST':
        post = PostManager()
        print(list(request.form.keys()))
        user = UserManager.load_models[session['username']]
        post.save_post(request.form, user)
    return render_template('home.html')

@app.route('/edit', methods=['GET','POST'])
@login_required
def edit():
    context = {}
    user = UserManager.load_models[session['username']]
    context['user'] = user
    if request.method == 'POST':
        user.getModelFromForm(request.form)
        user.save()
    return render_template('edit.html', context=context)
if __name__ == '__main__':
    app.run(debug=True)
