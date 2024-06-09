import sqlite3

from flask import Blueprint, render_template, redirect, url_for,session,flash
from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, EqualTo

import server

authentication_bp = Blueprint("authentication", __name__, template_folder="templates")


class User(UserMixin):
    def __init__(self, id: int, email: str, password: str):
        self.id = id
        self.email = email
        self.password = password

    @staticmethod
    def get(user_id: int):
        user_row = server.run_query(f"select * from users where id={user_id}")
        return user_row

    @staticmethod
    def create(email: str, password: str):
        try:
            hashed_password = generate_password_hash(password).decode().replace("$2b$12$","")
            server.run_query(f"insert into users (email,password) values ('{email}','{hashed_password}')")
            return True
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                return False
            else:
                raise e
    @staticmethod
    def search_user(email,password):
        hashed_password = generate_password_hash(password).decode().replace("$2b$12$","")
        try:
            server.run_query(f"select * from users where email='{email}' and password='{hashed_password}'")
            return True
        except:
            pass
    def __str__(self) -> str:
        return f"<Id: {self.id},Email: {self.email}>"


class LoginForm(FlaskForm):
    email = StringField(validators=[
        InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "E-mail"})
    password = PasswordField(validators=[
        InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Mot de passe"})
    remember_me=BooleanField("Remember Me")
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField(validators=[
        InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "E-mail"})
    password = PasswordField(validators=[
        InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Mot de passe"})
    password2 = PasswordField(
        validators=[InputRequired(), EqualTo('password', message='Les mots de passe doivent être identiques!')],
        render_kw={"placeholder": "Répétez le mot de passe"})
    submit = SubmitField('Register')


@authentication_bp.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        found=User.search_user(email=form.email.data,password=form.password.data)
        if found:
            if form.remember_me.data:
                session.permanent = True
            session["user"]={"user_email":form.email.data}
            return redirect(url_for("home_page"))
    return render_template("login.html", form=form)

@authentication_bp.route("/register", methods=["GET", "POST"])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        success = User.create(email=form.email.data, password=form.password.data)
        if success:
            flash('Registration successful! Please login.', 'error')
            return redirect(url_for('authentication.login_page'))
        else:
            flash('Email already in use. Please use a different email.', 'danger')
    return render_template("register.html", form=form)

@authentication_bp.route("/logout")
def logout_page():
    session.pop("user",None)
    return "Logged out successfully ! "
@authentication_bp.route("/user")
def user():
    if "user" in session:
        user=session["user"]["user_email"]
        return f"<h1>{user}</h1>"
    else:
        return "<h1>pb</h1>"
