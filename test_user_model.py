import os
from unittest import TestCase

from sqlalchemy import exc

from models import Calendar, List, Meal, User, db

os.environ["DATABASE_URL"] = "postgresql:///meal_planning_db_test"

from app import app

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages"""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User(
            username="test1",
            password="password",
            first_name="John",
            last_name="Doe",
            email="email@email.com",
        )
        uRegister = User.register(u1)
        uid1 = 1111
        uRegister.id = uid1

        u2 = User(
            username="test2",
            password="password",
            first_name="John",
            last_name="Doe",
            email="email2@email.com",
        )
        u2Register = User.register(u2)
        uid2 = 2222
        u2Register.id = uid2

        db.session.add_all([uRegister, u2Register])
        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does the model work?"""

        u = User(
            username="testuser",
            password="HASHED_PASSWORD",
            first_name="John",
            last_name="Doe",
            email="test@test.com",
        )
        db.session.add(u)
        db.session.commit()

        # User shouldn't have any meals added
        self.assertEqual(len(u.todo_list), 0)

    def test_user_signup(self):
        u_test = User(
            username="testtesttest",
            password="password",
            first_name="John",
            last_name="Doe",
            email="test@test.com",
        )
        u_testregistered = User.register(u_test)
        uid = 999999
        u_testregistered.id = uid
        db.session.add(u_testregistered)
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.id, uid)
        self.assertEqual(u_test.username, "testtesttest")
        self.assertEqual(u_test.email, "test@test.com")
        self.assertEqual(u_test.first_name, "John")
        self.assertEqual(u_test.last_name, "Doe")
        self.assertNotEqual(u_test.password, "password")
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_valid_authentication(self):
        u = User.login(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)
