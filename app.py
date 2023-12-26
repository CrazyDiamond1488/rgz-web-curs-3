from flask import Flask, redirect, url_for, render_template, Blueprint, request
from Db import db
from Db.models import users
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = '123'
user_db = 'yustinian_orm'
host_ip = '127.0.0.1'
host_port = '5432'
database_name = 'initiative_orm'
password = '123'

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}?client_encoding=UTF8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()

login_manager.login_view = 'rgz.login6'
login_manager.init_app(app)

@login_manager.user_loader
def load_users(user_id):
    return users.query.get(int(user_id))

# Перемещенный импорт
from rgz import rgz

app.register_blueprint(rgz)


