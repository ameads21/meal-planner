from flask import Flask, redirect, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Meal, Calendar, List
from forms import UserLoginForm, UserRegisterForm
from secrets import key
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgresql:///meal_planning_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', key)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return render_template('index.html')

################## USER LOGIN, REGISTER, LOGOUT ##################
@app.route('/register', methods=["GET", "POST"])
def register_user():
    form = UserRegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        new_user = User.register(username, password, first_name, last_name, email)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another')
            return render_template("register.html", form=form)
            
        session['user_id'] = new_user.id
        flash("Welcome! Successfully Created Your Account!", "success")
        return redirect('/')
    else:

        return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_user():
    form = UserLoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.login(username, password)
        if user:
            flash(f"Welcome back {user.username}!", "success")
            session['user_id'] = user.id
            return redirect(f'/users/{user.id}')
        else:
            form.username.errors = ['Invalid username/password']

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash("Successfully logged out", "primary")
    return redirect('/')


################## USER PAGES ##################
@app.route('/users/<int:user_id>')
def user_page(user_id):
    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    user = User.query.get_or_404(user_id)
    if user.id == session['user_id']:
        return render_template("user.html", user=user)