import os
from unittest import TestCase
from models import db, User, Meal, List, Calendar
from bs4 import BeautifulSoup

os.environ['DATABASE_URL'] = 'postgresql:///meal_planning_db_test'

from app import app, CURR_USER

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class MessageViewTestCase(TestCase):
    """Test views for messages."""
    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.register(User(username="test1", password="password", first_name="John", last_name="Doe", email="email@email.com"))
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id
        
        self.u1 = User(username="testtesttest", password="password", first_name="John", last_name="Doe", email="test@test.com")
        self.u1_id = 778
        self.u1.id = self.u1_id
        self.u2 = User.register(User(username="test2", password="password", first_name="John", last_name="Doe", email="email2@email.com"))
        self.u2_id = 884
        self.u2.id = self.u2_id
        self.u3 = User.register(User(username="test3", password="password", first_name="John", last_name="Doe", email="email3@email.com"))
        self.u4 = User.register(User(username="test4", password="password", first_name="John", last_name="Doe", email="email4@email.com"))

        db.session.add_all([self.u1, self.u2, self.u3, self.u4])
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    
    def test_users_profile(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER] = self.u1_id
            resp = c.get(f"/users/{self.u1_id}")
            self.assertIn('<p><b>Username</b></p>', str(resp.data))
            self.assertEqual(resp.status_code, 200)

    
    def test_todo_page(self):
        todo = List(item="Fish", user_id=self.u1_id)
        db.session.add(todo)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER] = self.u1_id
            resp = c.get(f"/users/{self.u1_id}/shopping-list")
            self.assertIn('Fish', str(resp.data))
            self.assertEqual(resp.status_code, 200)

    def test_calendar_page(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER] = self.u1_id
            resp = c.get(f"/users/{self.u1_id}/calendar")
            self.assertIn('Meal Calendar', str(resp.data))
            self.assertEqual(resp.status_code, 200)

    def test_search_page(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER] = self.u1_id
            resp = c.get(f"/users/{self.u1_id}/search?search=chicken")
            self.assertIn('Search results for chicken', str(resp.data))
            self.assertEqual(resp.status_code, 200)

            #No results found page
            resp = c.get(f"/users/{self.u1_id}/search?search=test")
            self.assertIn('No results for test', str(resp.data))
            self.assertEqual(resp.status_code, 200)