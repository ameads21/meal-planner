from flask import Flask, redirect, render_template, session, flash, g, request
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Meal, Calendar, List
from forms import UserLoginForm, UserRegisterForm, UserEditForm
from secrets import key
from sqlalchemy.exc import IntegrityError
import os

CURR_USER = 'user_id'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgresql:///meal_planning_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', key)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.before_request
def add_user_to_g():
    """If logged in, add current user to Flask global"""

    if CURR_USER in session:
        g.user = User.query.get_or_404(session[CURR_USER])
    else:
        g.user = None

def do_login(user):
    """Logging in user"""
    session[CURR_USER] = user.id


def do_logout():
    """Logout User"""
    if CURR_USER in session:
        del session[CURR_USER]


def do_user_check(check_user):
    """Check session for logged in user"""
    if not g.user:
        flash("Please login first!", "danger")
        return "Denied"

    if check_user.id != session['user_id']:
        flash("Access Denied!", "danger")
        return "Denied"

    return None

@app.route('/')
def home_page():
    if not g.user:
        return render_template('index.html')
    
    return redirect(f'/users/{g.user.id}')

################## USER LOGIN, REGISTER, LOGOUT ##################
@app.route('/register', methods=["GET", "POST"])
def register_user():
    form = UserRegisterForm()
    if form.validate_on_submit():
        try:
            data = {k: v for k, v in form.data.items() if k != "csrf_token"}
            new_user = User(**data)
            register_user = User.register(new_user)
            db.session.add(register_user)
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another')
            return render_template("register.html", form=form)
            
        session['user_id'] = register_user.id
        flash("Welcome! Successfully Created Your Account!", "success")
        return redirect(f'/users/{register_user.id}')
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
            do_login(user)
            flash(f"Welcome back {user.username}!", "success")
            return redirect(f'/users/{user.id}')
        else:
            form.username.errors = ['Invalid username/password']

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    do_logout()
    flash("Successfully logged out", "primary")
    return redirect('/')


################## USER PAGE, DELETE, EDIT ##################
@app.route('/users/<int:user_id>')
def user_page(user_id):
    user = User.query.get_or_404(user_id)
    check_user = do_user_check(user)
    if check_user == None:
        return render_template("user.html", user=user)
    else:
        return redirect("/")


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def user_delete(user_id):
    user = User.query.get_or_404(user_id)
    check_user = do_user_check(user)
    if check_user == None:
        do_logout()
        db.session.delete(g.user)
        db.session.commit()
        flash("We hope you come back soon!", "success")
        return redirect('/register')
    else:
        return redirect("/")

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    check_user = do_user_check(user)
    if check_user == None:
        if form.validate_on_submit():
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.email = form.email.data
            db.session.add(user)
            db.session.commit()
            flash("Updated!", "success")
            return redirect(f'/users/{user.id}')
        else:
            return render_template('user_edit.html', form=form)
    else:
        return redirect("/")
    

    
################## NAVBAR LINK/SEARCH ##################

@app.route('/search', methods=["POST"])
def search_engine():
    search_input = request.form['search']
    flash (f"Search results for {search_input}")
    return redirect('/')

@app.route('/users/<int:user_id>/calendar')
def meal_calendar(user_id):
    user = User.query.get_or_404(user_id)
    check_user = do_user_check(user)
    return render_template("user_meal_calendar.html", user=user)


@app.route('/users/<int:user_id>/saved-meals')
def saved_meals(user_id):
    user = User.query.get_or_404(user_id)
    check_user = do_user_check(user)
    return render_template("user_saved_meals.html", user=user)

@app.route('/users/<int:user_id>/shopping-list')
def shopping_list(user_id):
    user = User.query.get_or_404(user_id)
    check_user = do_user_check(user)
    return render_template("user_shopping_list.html", user=user)