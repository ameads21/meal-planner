from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length

class UserLoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(message="This form is required!")])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6)])


class UserRegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(message="This form is required!")])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6)])
    first_name = StringField("First Name", validators=[InputRequired(message="This form is required!")])
    last_name = StringField("Last Name", validators=[InputRequired(message="This form is required!")])
    email = StringField('E-mail', validators=[InputRequired(), Email()])