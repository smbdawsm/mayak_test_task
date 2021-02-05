from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models import users_db

from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
import requests
import json

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['post'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    # user = User.query.filter_by(email=email).first()

    # if not user or not check_password_hash(user.password, password):
    #     flash('Please check your login details and try again.')
    #     return redirect(url_for('auth.login')) # 
    url = 'http://136.243.111.3:8000/api/auth/login?admin=1&api=54jfGJHD32dh56jcvb87'
    try:
        json_data = {
            "email": email,
            "password": password,
            "user_data": "const"
        }

        x = requests.get(url, json=json_data)
        t = json.loads(x.text)
        
        if 'success' in t:
            data = t['user']
            try:
                new_user = User(email=data['email'], name=data['email'], password=generate_password_hash("1", method='sha256'))
            
                check_for_user = User.query.filter_by(email=data['email']).first()
                if (check_for_user):
                    users_db.session.delete(check_for_user)
                    users_db.session.commit()
                users_db.session.add(new_user)
                users_db.session.commit()
                login_user(new_user, remember=remember)
            except Exception as err:
                print(err)
                flash('Please check your login details and try again.')
            return redirect(url_for('views.get_all_servers_view'))
        else:
            flash('Please check your login details and try again.')
    except Exception as err:
        print(err)
        flash('Please check your login details and try again.')
    return redirect(url_for('auth.login'))


    

@auth.route('/', methods=['post', 'get'])
@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/signup')
def signup():
    return render_template('signup.html', name=current_user.name)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['post'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user: 
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    users_db.session.add(new_user)
    users_db.session.commit()

    return redirect(url_for('views.get_all_servers_view'))