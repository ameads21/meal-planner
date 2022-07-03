import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Meal, List, Calendar
os.environ['DATABASE_URL'] = 'postgresql:///meal_planning_db_test'

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages"""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u = User(username="test1", password="password", first_name="John", last_name="Doe", email="email@email.com")
        uRegister = User.register(u)
        uid = 1111
        uRegister.id = uid

        t = List(item="testSauce", user_id=uid)
        tid = 9999
        t.id = tid

        db.session.add(uRegister)
        db.session.commit()
        
        db.session.add(t)
        db.session.commit()

        u = User.query.get(uid)
        t = List.query.get(tid)

        self.u = u
        self.uid = uid

        self.t = t
        self.tid = tid

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_list_model(self):
        todo = List(item="testSauce", user_id=self.uid)
        db.session.add(todo)
        db.session.commit()

        self.assertEqual(len(self.u.todo_list), 2)

    def test_list_delete(self):
        db.session.delete(self.t)
        db.session.commit()

        self.assertEqual(len(self.u.todo_list), 0)

    def test_list_marked(self):
        self.t.checked = True
        db.session.add(self.t)
        db.session.commit()

        marked_t = List.query.get(self.tid)

        self.assertEqual(marked_t.checked, True)