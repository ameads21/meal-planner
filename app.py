from flask import Flask, redirect, render_template, session, flash, g, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Meal, Calendar, List
from forms import UserLoginForm, UserRegisterForm, UserEditForm, UserMealCalendarForm, UserListForm, UserMealCalenderDateForm
from sqlalchemy.exc import IntegrityError
import os
import json
import datetime
import requests
import calendar

CURR_USER = 'user'
API_BASE_URL = "https://www.themealdb.com/api/json/v1/1"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgresql:///meal_planning_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "secret")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

# toolbar = DebugToolbarExtension(app)

def myconverter(obj):
   return f"{obj.year}-{obj.month}-{obj.day}"

@app.before_request
def add_user_to_g():
    """If logged in, add current user to Flask global"""

    if CURR_USER in session:
        g.user = session[CURR_USER]
    else:
        g.user = None

def do_login(user):
    """Logging in user"""
    data = {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email
    }

    session[CURR_USER] = data
    g.user = session[CURR_USER]




def do_logout():
    """Logout User"""
    if CURR_USER in session:
        del session[CURR_USER]


def do_user_check(check_user):
    """Check session for logged in user"""
    if not g.user:
        flash("Please login first!", "danger")
        return False

    if check_user != session[CURR_USER]['id']:
        flash("Access Denied!", "danger")
        return False

    return True

@app.route('/')
def home_page():
    if not g.user:
        return render_template('index.html')
    return redirect(f'/users/{g.user["id"]}/calendar')

################## USER LOGIN, REGISTER, LOGOUT ##################
@app.route('/register', methods=["GET", "POST"])
def register_user():
    form = UserRegisterForm()
    if form.validate_on_submit():
        try:
            data = {k: v for k, v in form.data.items() if k != "csrf_token"}
            new_user = User.register(User(**data))
            User.save(new_user)
        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another')
            return render_template("register.html", form=form)
            
        do_login(new_user)
        flash("Welcome! Successfully Created Your Account!", "success")
        return redirect(f'/users/{new_user.id}/calendar')
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
            return redirect(f'/users/{g.user["id"]}/calendar')
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
    check_user = do_user_check(user_id)
    if check_user:
        return render_template("user.html")
    else:
        return redirect("/")


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def user_delete(user_id):
    check_user = do_user_check(user_id)
    if check_user:
        User.delete(User.query.get_or_404(g.user['id']))
        do_logout()
        flash("We hope you come back soon!", "success")
        return redirect('/register')
    else:
        return redirect("/")

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def user_edit(user_id):
    check_user = do_user_check(user_id)
    if check_user:
        temp_user = User(first_name=g.user['first_name'], last_name=g.user['last_name'], email=g.user['email'])
        form = UserEditForm(obj=temp_user)
        if form.validate_on_submit():
            g.user['first_name'] = form.first_name.data
            g.user['last_name'] = form.last_name.data
            g.user['email'] = form.email.data
            User.update(g.user)
            flash("Updated!", "success")
            return redirect(f'/users/{g.user["id"]}')
        else:
            return render_template('user_edit.html', form=form)
    else:
        return redirect("/")

    
################## NAVBAR SEARCH ##################

@app.route('/users/<int:user_id>/search', methods=['GET'])
def search_engine(user_id):
    check_user = do_user_check(user_id)
    if check_user:
        search_input = request.args['search'] 
        res = requests.get(f"{API_BASE_URL}/search.php?s={search_input}")
        data = res.json()
        return render_template("search.html", data=data['meals'], search_input=search_input)
    else:
        return redirect('/')


################## Meal Calendar ##################

@app.route('/users/<int:user_id>/calendar')
def meal_calendar(user_id):
    check_user = do_user_check(user_id)
    if check_user:
        return render_template("user_meal_calendar.html")
    else:
        flash("Access Denied!", "danger")
        return redirect('/')


@app.route('/users/<int:user_id>/add-meal', methods=['GET', 'POST'])
def add_own_meal(user_id):
    check_user = do_user_check(user_id)
    if check_user:
        form = UserMealCalendarForm()
        if form.validate_on_submit():
            meal_name = form.meal_name.data
            dateSelected = myconverter(form.date.data)
            dateInfo = Calendar(user_id=user_id, meal_name=meal_name, selected_date=dateSelected )
            Calendar.save(dateInfo)
            return redirect(f'/users/{user_id}/calendar')
        else:
            return render_template('meal_add.html', form=form)
    else:
        return redirect('/')


@app.route('/users/<int:user_id>/calendar', methods=['POST'])
def create_calendar(user_id):
    check_user = do_user_check(user_id)
    if check_user:
        c = calendar.HTMLCalendar(calendar.SUNDAY)
        mealList = []
        meals = Calendar.query.filter(Calendar.selected_date.like(f"{request.json['year']}-{request.json['month']}-%")).filter(Calendar.user_id == user_id).all()
        for m in meals:
            mealInfo = {
                "id": m.id,
                "user_id": user_id,
                "meal_id": m.meal_id,
                "meal_name": m.meal_name,
                "date": m.selected_date
            }
            mealList.append(mealInfo)
        data = {
            "calendar": c.formatmonth(request.json['year'], request.json['month']),
            "meals": mealList,
        }
        return data
    else:
        return redirect('/')

@app.route('/users/<int:user_id>/calendar/add/<int:meal_id>/<meal_name>', methods=['GET', 'POST'])
def add_recipe(user_id, meal_id, meal_name):
    check_user = do_user_check(user_id)
    if check_user:
        form = UserMealCalenderDateForm()
        if form.validate_on_submit():
            new_meal = Calendar(user_id=user_id, meal_id=meal_id, meal_name=meal_name, selected_date=form.date.data)
            Calendar.save(new_meal)
            flash("Saved meal to calendar", "success")
            return redirect(f'/users/{user_id}/meals/{meal_id}/view/{meal_name}')
        else:
            return render_template('create_meal_calendar.html', form=form, meal_id=meal_id, meal_name=meal_name)
    else:
        return redirect('/')

@app.route('/users/<int:user_id>/calendar/delete/<int:meal_id>', methods=['POST'])
def delete_calendar_meal(user_id, meal_id):
    check_user = do_user_check(user_id)
    if check_user:
        meal = Calendar.query.get_or_404(meal_id)
        Calendar.delete(meal)
        return redirect(f'/users/{user_id}/calendar')
    else:
        return redirect('/')


################## Todo/Shopping List ##################

@app.route('/users/<int:user_id>/shopping-list', methods=['GET', 'POST'])
def shopping_list(user_id):
    check_user = do_user_check(user_id)
    if check_user:
        form = UserListForm()
        if form.validate_on_submit():
            new_todo = List(item=form.item.data, user_id=user_id)
            List.save(new_todo)
            flash(f"Successfully created {new_todo.item}!", "success")
            return redirect(f'/users/{user_id}/shopping-list')
        else:
            todo_list = List.query.filter_by(user_id=user_id).order_by(List.checked)
            return render_template('user_shopping_list.html', form=form, todo_list=todo_list)
    else:
        return redirect("/")
#Ended here!!
@app.route('/users/<int:user_id>/shopping-list/<int:list_id>/delete', methods=['POST'])
def delete_todo(list_id, user_id):
    check_user = do_user_check(user_id)
    if check_user:
        todo_item = List.query.get_or_404(list_id)
        List.delete(todo_item)
        return redirect(f"/users/{user_id}/shopping-list")
    else:
        return redirect('/')

@app.route('/users/<int:user_id>/shopping-list/add', methods=['POST'])
def add_todo(user_id):
    check_user = do_user_check(user_id)
    if check_user:
        new_todo = List(user_id=user_id, item=request.json['ingredient'])
        List.save(new_todo)
        flash("Added to grocery list", "success")
        return redirect('/')
    else:
        return redirect('/')

@app.route('/users/<int:user_id>/shopping-list/<int:list_id>', methods=['POST'])
def mark_todo(user_id, list_id):
    check_user = do_user_check(user_id)
    if check_user:
        todo = List.query.get_or_404(list_id)
        todo.checked = not todo.checked
        
        List.save(todo)
        return redirect(f'/users/{user_id}/shopping-list')
    else:
        return redirect('/')


################## Meal Information ##################

@app.route("/users/<int:user_id>/meals/<int:meal_id>/view/<meal_name>")
def meal_info(user_id, meal_id, meal_name):
    check_user = do_user_check(user_id)
    if check_user:
        res = requests.get(f"{API_BASE_URL}/lookup.php?i={meal_id}")
        data = res.json()
        saved_meal = Meal.query.filter(Meal.meal_id == meal_id, Meal.user_id == user_id).one_or_none()
        ingredients = []
        measure = []
        
        for k, v in data['meals'][0].items():
            if k.startswith("strIngredient"):
                if v != '' and v!= None:
                    ingredients.append(v)
            if k.startswith("strMeasure"):
                if v == '':
                    measure.append(None)
                else:
                    measure.append(v)

        directions = data['meals'][0]['strInstructions'].split('\r\n')
        
        recipeIngredients = list(zip(measure, ingredients))
        return render_template("meal_info.html", user_id=user_id, data=data['meals'][0], recipeIngredients=recipeIngredients, saved_meal=saved_meal, directions=directions, ingredients=ingredients, measure=measure)
    else:
        return redirect('/')




################## Saved Meals ##################


@app.route('/users/<int:user_id>/saved-meals', methods=['GET'])
def saved_meals(user_id):
    check_user = do_user_check(user_id)
    if check_user:
        saved_meals = Meal.query.filter_by(user_id=user_id)
        return render_template("user_saved_meals.html", saved_meals=saved_meals)
    else:
        return redirect('/')

@app.route('/users/<int:user_id>/meals/<int:meal_id>/view/<meal_name>', methods=['POST'])
def adding_saved_meal(user_id, meal_id, meal_name):
    check_user = do_user_check(user_id)
    if check_user:
        saved_meal = Meal(user_id=user_id, meal_id=meal_id, meal_name=meal_name, meal_image=request.json['meal_image'])
        Meal.save(saved_meal)
        flash("Meal saved!", "success")
        return redirect(f'/users/{user_id}/meals/{meal_id}/view/{meal_name}')
    else:
        return redirect("/")

@app.route('/users/<int:user_id>/saved-meals/<int:meal_id>/delete', methods=['POST'])
def deleting_saved_meal(user_id, meal_id):
    check_user = do_user_check(user_id)
    if check_user:
        meal = Meal.query.filter(Meal.meal_id == meal_id, Meal.user_id == user_id).first()
        Meal.delete(meal)
        flash(f"Successfully deleted", "success")
        return redirect(f'/users/{user_id}/saved-meals')
    else:
        return redirect("/")

