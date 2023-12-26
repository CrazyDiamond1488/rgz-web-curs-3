from flask import Blueprint, redirect, url_for, render_template, request, session
from Db import db

from Db.models import users, initiative
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, current_user, logout_user

rgz = Blueprint('rgz', __name__)


@rgz.route('/rgz/glav')
def rgz_glav():
    username_form = session.get('username')
    return render_template('glav6.html', username = username_form)


@rgz.route('/rgz/register', methods = ['GET', 'POST'])
def register():
    errors = []
    if request.method == 'GET':
        return render_template('register6.html')
    
    username_form = request.form.get('username')
    password_form = request.form.get('password')

    isUserExist = users.query.filter_by(username=username_form).first()
    if isUserExist is not None:
        errors.append("Пользователь уже существует")
        return render_template('register6.html', errors=errors)   

    if not (username_form or password_form):
        errors.append("Пожалуйста заполните все поля")
        print(errors)
        return render_template('register6.html', errors=errors)
    if username_form == '':
        errors.append("Пожалуйста заполните все поля")
        print(errors)
        return render_template('register6.html', errors=errors)
    if password_form == '':
        errors.append("Пожалуйста заполните все поля")
        print(errors)
        return render_template('register6.html', errors=errors)
    
    if len(password_form) < 5:
            errors.append("Пароль должен содержать не менее 5 символов")
            print(errors)
            return render_template('register6.html', errors=errors)
        
    
    hashPassword = generate_password_hash(password_form, method='pbkdf2')
    newUser = users(username=username_form, password=hashPassword)

    db.session.add(newUser)
    db.session.commit()

    return redirect('/rgz/login')

@rgz.route('/rgz/login', methods=["GET", "POST"])
def login6():
    errors = []
    if request.method == "GET":
        return render_template("login6.html")
    
    username_form = request.form.get("username")
    password_form = request.form.get("password")

    if not (username_form and password_form):
            errors.append("Пожалуйста, заполните все поля")

    my_user = users.query.filter_by(username=username_form).first()
    if my_user is not None:
        
        if check_password_hash(my_user.password, password_form):
            login_user(my_user, remember=False)
            return redirect("/rgz/glav")
        
    return render_template("login6.html")

@rgz.route("/rgz/initiative", methods=['GET'])
def getInitiatives():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    initiatives = initiative.query.paginate(page=page, per_page=per_page, error_out=False)
    usernames = [users.query.get(initiative.user_id).username for initiative in initiatives.items]
    return render_template("articles6.html", initiatives=initiatives, usernames=usernames, users=users)


@rgz.route("/rgz/newarticle", methods=["GET", "POST"])
@login_required
def createArticle():
    if request.method == "GET":
        return render_template("newarticle6.html")

    text = request.form.get("text")
    title = request.form.get("title")

    if text is None or len(text) == 0:
        errors = ["Заполните текст"]
        return render_template("newarticle6.html", errors=errors)

    new_initiative = initiative(user_id=current_user.id, title=title, article_text=text)
        

    db.session.add(new_initiative)
    db.session.commit()
    
    return redirect("/rgz/initiative")



@rgz.route("/rgz/initiative/<int:article_id>", methods=['GET', 'POST'])
def getArticle(article_id):
    selected_initiative = initiative.query.get(article_id)

    if selected_initiative:
        if current_user.is_authenticated and (selected_initiative.user_id == current_user.id or selected_initiative.is_public):
            article_text = selected_initiative.article_text
            return render_template("6articles.html", initiative=selected_initiative, title=selected_initiative.title, username=current_user.username)

@rgz.route("/rgz/initiative/<int:article_id>/delete", methods=['POST'])
@login_required
def deleteArticle(article_id):
    selected_initiative = initiative.query.get(article_id)

    if selected_initiative:
        if selected_initiative.user_id == current_user.id:
            db.session.delete(selected_initiative)
            db.session.commit()
            return redirect("/rgz/initiative")
        else:
            return "Вы не можете удалить эту статью, так как вы не являетесь ее автором."
    else:
        return "Статья не найдена."

from flask import request

@rgz.route('/rgz/initiative/<int:article_id>/vote', methods=['POST'])
@login_required
def vote(article_id):
    vote_type = request.form.get('vote')
    article = initiative.query.get(article_id)

    if vote_type == 'up':
        article.likes = article.likes + 1 if article.likes else 1
    elif vote_type == 'down':
        article.likes = article.likes - 1 if article.likes else -1

    if article.likes <= -10:
        db.session.delete(article)

    db.session.commit()

    return redirect(url_for('rgz.getInitiatives'))

@rgz.route('/rgz/logout')
@login_required
def logout():
    logout_user()
    return redirect('/rgz/glav')
    

   