from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.fields.html5 import DateField
from wtforms.validators import Email, InputRequired, Length


class UserLoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(message="This form is required!")]
    )
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6)])


class UserRegisterForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(message="This form is required!")]
    )
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6)])
    first_name = StringField(
        "First Name", validators=[InputRequired(message="This form is required!")]
    )
    last_name = StringField(
        "Last Name", validators=[InputRequired(message="This form is required!")]
    )
    email = StringField("E-mail", validators=[InputRequired(), Email()])


class UserEditForm(FlaskForm):
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    email = StringField("E-mail")


class UserMealCalendarForm(FlaskForm):
    meal_name = StringField("Meal Name", validators=[InputRequired()])
    date = DateField("Meal Date", format="%Y-%m-%d", validators=[InputRequired()])


class UserMealCalenderDateForm(FlaskForm):
    date = DateField("Meal Date", format="%Y-%m-%d", validators=[InputRequired()])


class UserListForm(FlaskForm):
    item = StringField("Item", validators=[InputRequired()])
