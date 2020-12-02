from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)

    todo_list = db.relationship("List", backref="users", cascade="all, delete-orphan")
    meal_calendar = db.relationship("Calendar", backref="users", cascade="all, delete-orphan")
    saved_meals = db.relationship("Meal", backref="users", cascade="all, delete-orphan")

    @classmethod
    def register(cls, user):
        """Register the user with hashed password"""

        hashed = bcrypt.generate_password_hash(user.password)
        hashed_utf8 = hashed.decode('utf8')

        return cls(username=user.username, password=hashed_utf8, first_name=user.first_name, last_name=user.last_name, email=user.email)

    @classmethod
    def login(cls, username, pwd):

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False


class Meal(db.Model):
    __tablename__ = "meals"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    meal_id = db.Column(db.Integer, nullable=False)
    meal_name = db.Column(db.String, nullable=False)
    meal_image = db.Column(db.String, nullable=False)

class List(db.Model):

    __tablename__ = "lists"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item = db.Column(db.Text, nullable=False)
    checked = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Calendar(db.Model):

    __tablename__ = "calendar"
    def __repr__(self):
        return f"<Calendar {self.id} {self.user_id} {self.meal_id} {self.selected_date}>"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    meal_id = db.Column(db.Integer)
    meal_name = db.Column(db.String, nullable=False)
    selected_date = db.Column(db.String, nullable=False)