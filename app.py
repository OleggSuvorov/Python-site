# -*- coding:utf-8 -*-
from flask import Flask, request, render_template, redirect, url_for, session
from models.executeSqlite3 import executeSelectOne, executeSelectAll, executeSQL
from functools import wraps
from models.user_manager import UserManager
from models.user_type_manager import UserTypeManager
from models.base_manager import SNBaseManager
import os
import sqlite3

# створюємо головний об'єкт сайту класу Flask
from models.post_manager import PostManager

app = Flask(__name__)
# добавляємо секретний ключ для сайту щоб шифрувати дані сессії
# при кожнаму сапуску фласку буде генечитись новий рандомний ключ з 24 символів
#app.secret_key = os.urandom(24)
app.secret_key = '125'

conn = sqlite3.connect('my_db.sqlite3', check_same_thread=False)

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

@app.route('/add_friend', methods=['POST'])
@login_required
def add_friend():
    print(request.json)
    user_id = int(request.json['id'])
    print('fqqwrwefew2')
    user = UserManager.load_models[session['username']]
    user.add_friend(id=user_id)
    return redirect(request.referrer)

@app.route('/user/<username>')
@login_required
def user_search(username):
    username = username.split(' ')
    curs = conn.cursor()

    friend = curs.execute("select * from users where first_name = '{}' and last_name = '{}'".format(username[0], username[1])).fetchall()
    if not friend:
        user_model = user_info(curs, session['email'])
        context3 = {'user': user_model, 'name': '', 'email': 'nothing_found', 'age': '', 'phone':  '', 'sex': '', 'address': '', 'id': '', 'friends': friend, 'block': 'none'}
        return render_template('friends.html', **context3)
    if len(friend)>1:
        user_model = user_info(curs, session['email'])
        context3 = {'user': user_model, 'name': '', 'email': 'friends_list', 'age': '', 'phone':  '', 'sex': '', 'address': '', 'id': '', 'friends': friend, 'block': 'none'}
        return render_template('friends.html', **context3)
    else:
        friend = friend[0]
        print(friend)

        #friend_add = curs.execute("select * from users_add where users = '{}'".format(friend[0])).fetchone()
        if session:
            current_email = session['username']
            current_id = curs.execute("select id from users where nickname = '{}'".format(current_email)).fetchone()
            f_col = curs.execute("select * from user_relation where user1 = '{}' and user2 = '{}'".format(current_id[0], friend[0])).fetchone()
            s_col = curs.execute("select * from user_relation where user1 = '{}' and user2 = '{}'".format(friend[0], current_id[0])).fetchone()
            print(f_col, s_col)
            if f_col:
                if_blocked = curs.execute("select block from user_relation where user1 = '{}' and user2 = '{}'".format(current_id[0], friend[0])).fetchone()
                sender_id = current_id[0]
            elif s_col:
                if_blocked = curs.execute("select block from user_relation where user1 = '{}' and user2 = '{}'".format(current_id[0], friend[0])).fetchone()
                sender_id = friend[0]
            else:
                if_blocked = [None]
                sender_id = None
        else:
            current_id=None
            if_blocked = [None]
            sender_id = None
        Boulean = FriendConnectionValidation(curs, friend, current_id)
        print('qweqrwrwq', Boulean)
        selectUser = UserManager()
        selectUser.select().And([('nickname','=',current_email)]).run()
        context = {'user': selectUser,'name': friend[1] + ' ' + friend[2],'friend': friend, 'friends': Boulean, 'if_blocked': if_blocked[0], 'sender_id': sender_id, 'current_id': str(current_id[0])}
        return render_template('friend.html', context=context)


def FriendConnectionValidation(curs, friend, current_id):
    print(current_id, friend)
    if current_id:
        FriendConnectionValidation = curs.execute("select * from user_relation where user1 = '{}' and user2 = '{}'".format(current_id[0], friend[0])).fetchone()

        FriendConnectionValidation2 = curs.execute("select * from user_relation where user1 = '{}' and user2 = '{}'".format(friend[0], current_id[0])).fetchone()

        if FriendConnectionValidation:
            status = curs.execute("select block from user_relation where user1 = '{}' and user2 = '{}'".format(current_id[0], friend[0])).fetchone()[0]
            print(status)
            if status == 0 or status == 1:
                Boulean = True
            elif status == 'waiting':
                Boulean = 'waiting'
            else:
                Boulean = 'undefined'
        elif FriendConnectionValidation2:
            status = curs.execute("select block from user_relation where user2 = '{}' and user1 = '{}'".format(current_id[0], friend[0])).fetchone()[0]
            if status == 0 or status == 1:
                Boulean = True
            elif status == 'waiting':
                Boulean = 'waiting'
            else:
                Boulean ='undefined'
        else:
            Boulean = False
        print(Boulean)
        return Boulean
    else:
        Boulean = 'NotLoggedIn'
        return Boulean



     elif s_col:
            curs.execute("UPDATE name SET block = 'waiting' WHERE user1_id  = '{}' and user2_id  = '{}'".format(user2_id, user1_id)).fetchone()
            curs.execute("UPDATE name SET sender_id = '{}' WHERE user1_id  = '{}' and user2_id  = '{}'".format(user2_id, user2_id, user1_id)).fetchone()
            conn.commit()
        else:
            return redirect(url_for('return_home'))

        user_model = user_info(curs, session['email'])
        notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
        notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
        if notifications_id[0] == None:
            notifications = []
            print('none')
        else:
            notifications_id = notifications_id[0].split(',')
        context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'messages': 'Succesfully unfriended!', 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
        return jsonify({ 'status': 'unfriended' })
    elif action == "block":
        curs = conn.cursor()
        user1_id = curs.execute("SELECT id from users WHERE email ='{}'".format(session['email'])).fetchone()[0]
        user2_id = id
        f_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user1_id, user2_id)).fetchone()
        s_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user2_id, user1_id)).fetchone()
        friend_name1 = curs.execute("select first_name from users where id = '{}'".format(user2_id)).fetchone()
        friend_name2 = curs.execute("select last_name from users where id = '{}'".format(user2_id)).fetchone()

        if s_col:
            curs.execute("UPDATE name SET block = 1 WHERE user1_id  = '{}' and user2_id  = '{}'".format(user2_id, user1_id)).fetchone()
            conn.commit()
        elif f_col:
            curs.execute("UPDATE name SET block = 1 WHERE user1_id  = '{}' and user2_id  = '{}'".format(user1_id, user2_id)).fetchone()
            conn.commit()
        else:
            if user1_id:
                curs.execute("INSERT INTO name ('user1_id', 'user2_id', 'block', 'sender_id') VALUES('{}','{}','{}','{}')" \
                .format(user1_id, user2_id, 1, user1_id))
                conn.commit()
            else:
                return redirect(url_for('return_home'))

        user_model = user_info(curs, session['email'])
        notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
        notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
        if notifications_id[0] == None:
            notifications = []
            print('none')
        else:
            notifications_id = notifications_id[0].split(',')
        context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'messages': 'Succesfully blocked ' + str(friend_name1[0] + ' ' + friend_name2[0]) + ' !', 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
        return jsonify({ 'status': 'blocked' })
    elif action == "unblock":
        curs = conn.cursor()
        user1_id = curs.execute("SELECT id from users WHERE email ='{}'".format(session['email'])).fetchone()[0]
        user2_id = id
        f_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user1_id, user2_id)).fetchone()
        s_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user2_id, user1_id)).fetchone()
        friend_name1 = curs.execute("select first_name from users where id = '{}'".format(user2_id)).fetchone()
        friend_name2 = curs.execute("select last_name from users where id = '{}'".format(user2_id)).fetchone()

        if s_col:
            status = curs.execute("select sender_id from name where user1_id = '{}' and user2_id = '{}'".format(user2_id, user1_id)).fetchone()[0]
            print(status)
            if status == 'egal':
                curs.execute("UPDATE name SET block = 0 WHERE user1_id  = '{}' and user2_id  = '{}'".format(user2_id, user1_id)).fetchone()
            else:
                curs.execute("UPDATE name SET block = 'waiting' WHERE user1_id  = '{}' and user2_id  = '{}'".format(user2_id, user1_id)).fetchone()
            conn.commit()
        elif f_col:
            status = curs.execute("select sender_id from name where user1_id = '{}' and user2_id = '{}'".format(user1_id, user2_id)).fetchone()[0]
            print('status:', status)
            if status == 'egal':
                curs.execute("UPDATE name SET block = 0 WHERE user1_id  = '{}' and user2_id  = '{}'".format(user1_id, user2_id)).fetchone()
            else:
                print('second')
                curs.execute("UPDATE name SET block = 'waiting' WHERE user1_id  = '{}' and user2_id  = '{}'".format(user1_id, user2_id)).fetchone()
            conn.commit()
        else:
            return redirect(url_for('return_home'))

        user_model = user_info(curs, session['email'])
        notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
        notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
        if notifications_id[0] == None:
            notifications = []
            print('none')
        else:
            notifications_id = notifications_id[0].split(',')
        context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'messages': 'Succesfully unblocked ' + str(friend_name1[0] + ' ' + friend_name2[0]) + ' !', 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
        return jsonify({ 'status': 'unblocked' })
    elif action == "redo_request":
        curs = conn.cursor()
        user1_id = curs.execute("SELECT id from users WHERE email ='{}'".format(session['email'])).fetchone()
        if not user1_id:
            return redirect(url_for('return_home'))
        user1_id = user1_id[0]
        user2_id = id
        f_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user1_id, user2_id)).fetchone()
        s_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user2_id, user1_id)).fetchone()
        friend_name1 = curs.execute("select first_name from users where id = '{}'".format(user2_id)).fetchone()
        friend_name2 = curs.execute("select last_name from users where id = '{}'".format(user2_id)).fetchone()

        if s_col:
            curs.execute("DELETE FROM name WHERE user1_id = '{}' and  user2_id  = '{}'".format(user2_id, user1_id))
            conn.commit()
        elif f_col:
            curs.execute("DELETE FROM name WHERE user2_id = '{}' and  user1_id  = '{}'".format(user2_id, user1_id))
            conn.commit()
        else:
            return redirect(url_for('return_home'))

        f_name = curs.execute("SELECT first_name from users WHERE id ='{}'" \
                .format(user1_id)).fetchone()
        l_name = curs.execute("SELECT last_name from users WHERE id ='{}'" \
                              .format(user1_id)).fetchone()
        user_from = 'friend request from ' + str(f_name[0]) + ' ' + str(l_name[0])

        notific_id = curs.execute("SELECT id from notifications WHERE text ='{}' and receiver_id = '{}'" \
                              .format(user_from, user2_id)).fetchone()[0]
        notifications = curs.execute("SELECT notifications from users WHERE id ='{}'" \
                              .format(user2_id)).fetchone()[0]
        notifications = notifications.split('{},'.format(notific_id))
        new_string = ''
        for i in notifications:
            if i:
                new_string = new_string + i

        notifications = new_string

        print(notifications)
        curs.execute("UPDATE users SET notifications = '{}' WHERE id  = '{}'" \
                     .format(notifications, user2_id))

        curs.execute("DELETE FROM notifications WHERE text = '{}' and  receiver_id  = '{}'" \
                 .format(user_from, user2_id))
        conn.commit()



        user_model = user_info(curs, session['email'])
        notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
        notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
        if notifications_id[0] == None:
            notifications = []
            print('none')
        else:
            notifications_id = notifications_id[0].split(',')
        context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'messages': 'Succesfully canceled friend request!', 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
        return jsonify({ 'status': 'request redo' })
    elif action == "accept":
        type = request.json['type']
        curs = conn.cursor()
        if type == "profile_accept":
            user1_id = curs.execute("SELECT id from users WHERE email ='{}'".format(session['email'])).fetchone()
            if not user1_id:
                return redirect(url_for('return_home'))
            user1_id = user1_id[0]
            user2_id = id
        else:
            notific_id = request.args.get('notific_id')
            user1_id = curs.execute("SELECT sender_id from notifications WHERE id ='{}'".format(notific_id)).fetchone()
            print(user1_id, notific_id)
            if user1_id == None and notific_id == '0':
                user1_id = curs.execute("SELECT id from users WHERE email ='{}'".format(session['email'])).fetchone()[0]
            elif user1_id != None and notific_id != '0':
                user1_id = curs.execute("SELECT sender_id from notifications WHERE id ='{}'".format(notific_id)).fetchone()[0]
            else:
                return redirect(url_for('return_home'))

            user2_id = id

            print(user1_id, user2_id)
        f_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user1_id, user2_id)).fetchone()
        s_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user2_id, user1_id)).fetchone()
        if s_col:
            curs.execute("UPDATE name SET block = 0 WHERE user1_id  = '{}' and user2_id  = '{}'".format(user2_id, user1_id)).fetchone()
            curs.execute("UPDATE name SET sender_id = 'egal' WHERE user1_id  = '{}' and user2_id  = '{}'".format(user2_id, user1_id)).fetchone()
            conn.commit()
        elif f_col:
            curs.execute("UPDATE name SET block = 0 WHERE user1_id  = '{}' and user2_id  = '{}'".format(user1_id, user2_id)).fetchone()
            curs.execute("UPDATE name SET sender_id = 'egal' WHERE user1_id  = '{}' and user2_id  = '{}'".format(user1_id, user2_id)).fetchone()
            conn.commit()
        else:
            return redirect(url_for('return_home'))

        if type == "profile_accept":
            pass
            #curs.execute("DELETE FROM notifications WHERE id  = '{}'".format(notific_id)).fetchone()
        else:
            curs.execute("DELETE FROM notifications WHERE id  = '{}'".format(notific_id)).fetchone()

            notifications = curs.execute("SELECT notifications from users WHERE id ='{}'" \
                                  .format(user2_id)).fetchone()[0]
            notifications = notifications.split('{},'.format(notific_id))
            new_string = ''
            for i in notifications:
                if i:
                    new_string = new_string + i

            notifications = new_string

            curs.execute("UPDATE users SET notifications = '{}' WHERE id  = '{}'" \
                         .format(notifications, user2_id))

        conn.commit()
        user_model = user_info(curs, session['email'])
        notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
        notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
        if notifications_id[0] == None:
            notifications = []
            print('none')
        else:
            notifications_id = notifications_id[0].split(',')
        context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'messages': 'Friend request accepted!', 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
        return jsonify({ 'status': 'accepted' })
    elif action == "decline":
        curs = conn.cursor()
        notific_id = request.args.get('notific_id')

        user1_id = curs.execute("SELECT sender_id from notifications WHERE id ='{}'".format(notific_id)).fetchone()
        if not user1_id:
            return redirect(url_for('return_home'))
        user1_id = user1_id[0]
        user2_id = id

        curs.execute("DELETE FROM notifications WHERE id  = '{}'".format(notific_id)).fetchone()

        notifications = curs.execute("SELECT notifications from users WHERE id ='{}'" \
                              .format(user2_id)).fetchone()[0]
        notifications = notifications.split('{},'.format(notific_id))
        new_string = ''
        for i in notifications:
            if i:
                new_string = new_string + i

        notifications = new_string

        curs.execute("UPDATE users SET notifications = '{}' WHERE id  = '{}'" \
                     .format(notifications, user2_id))

        conn.commit()
        user_model = user_info(curs, session['email'])
        notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
        notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
        if notifications_id[0] == None:
            notifications = []
            print('none')
        else:
            notifications_id = notifications_id[0].split(',')
        context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'messages': 'Friend request declined!', 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
        return jsonify({ 'status': 'declined' })
    else: #become friends
        curs = conn.cursor()
        user1_id = curs.execute("SELECT id from users WHERE email ='{}'".format(session['email'])).fetchone()[0]
        user2_id = id

        FriendConnectionValidation = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user1_id, user2_id)).fetchone()
        FriendConnectionValidation2 = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user2_id, user1_id)).fetchone()
        if FriendConnectionValidation or FriendConnectionValidation2:
            return redirect(url_for('return_home'))
        else:
            curs.execute("INSERT INTO name ('user1_id', 'user2_id', 'block', 'sender_id') VALUES('{}','{}','{}','{}')" \
                .format(user1_id, user2_id, 'waiting', user1_id))
            f_name = curs.execute("SELECT first_name from users WHERE id ='{}'" \
                .format(user1_id)).fetchone()
            l_name = curs.execute("SELECT last_name from users WHERE id ='{}'" \
                                  .format(user1_id)).fetchone()
            user_from = 'friend request from ' + str(f_name[0]) + ' ' + str(l_name[0])
            print(user_from)
            curs.execute("INSERT INTO notifications ('text', 'receiver_id', 'sender_id') VALUES('{}', '{}', '{}')" \
                         .format(user_from, user2_id, user1_id))
            notific_id = curs.execute("SELECT id from notifications WHERE text ='{}' and receiver_id = '{}'" \
                                  .format(user_from, user2_id)).fetchone()[0]
            notifications = curs.execute("SELECT notifications from users WHERE id ='{}'" \
                                  .format(user2_id)).fetchone()[0]
            if notifications:
                notifications = str(notifications) + str(notific_id) + ','
            else:
                notifications = str(notific_id) + ','
            print(notifications)
            curs.execute("UPDATE users SET notifications = '{}' WHERE id  = '{}'" \
                         .format(notifications, user2_id))
            conn.commit()


            user_model = user_info(curs, session['email'])
            notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
            notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
            if notifications_id[0] == None:
                notifications = []
                print('none')
            else:
                notifications_id = notifications_id[0].split(',')
            context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'messages': 'Friend request succesfully sent!', 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
            return jsonify({ 'status': 'request sent' })

@app.route('/add_friend', methods=['GET'])
def add_friend():
    pass

#redirect(request.referrer)

@app.route('/upload', methods=['POST'])
def upload():
    type = request.args.get('type')
    user_type = request.args.get('user_type')
    curs = conn.cursor()

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
