"""User views tests."""

import os
from unittest import TestCase
from models import db, User, Message, Follows
from bs4 import BeautifulSoup


os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app
from app import app

# db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewsTestCase(TestCase):
    """Test views for User."""

    def setUp(self):
        """Create test client, add sample data."""

        u1 = User.signup("test_user_one", "test@test.com", "password", None)
        u1_id = 111
        u1.id = u1_id

        u2 = User.signup("test_user_two", "test2@test.com", "password", None)
        u2_id = 222
        u2.id = u2_id

        db.session.add_all([u1, u2])
        db.session.commit()

        u1 = User.query.get(u1_id)
        u2 = User.query.get(u2_id)

        self.u1 = u1
        self.u2 = u2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_signup_get(self):
        resp = self.client.get('/signup', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_signup_post(self):
        resp = self.client.post('/signup', data = {'username': 'test_user', 'email': 'fake@email.com', 'password': 'passw0rd'}, follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('test_user', html)
        self.assertIn('<h3>Log Messages</h3>', html)

    def test_loggin_(self):
        resp = self.client.post('/login', data = {'username': 'test_user_one', 'password': 'password'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def setup_likes(self):
        m1 = Message(text="testing one two three", user_id=self.u1.id)
        m2 = Message(text="four five six", user_id=self.u2.id)
        m3 = Message(id=1234, text="likable warble", user_id=self.u1.id)
        db.session.add_all([m1, m2, m3])
        db.session.commit()

        l1 = Likes(user_id=self.u1.id, message_id=1234)

        db.session.add(l1)
        db.session.commit()


    def test_add_like(self):
        msg = Message(id=2020, text="What a strange year", user_id=self.u1.id)
        db.session.add(msg)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.ui.id

        resp = c.post("/messages/2020/like", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        likes = Likes.query.filter(Likes.message_id==2020).all()
        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].user_id, self.u1.id)

    def test_user_show_with_likes(self):
        self.setup_likes()


        resp = self.client.get(f"/users/{self.u1.id}")
        soup = BeautifulSoup(resp.content, 'html.parser')

        self.assertIn("one two three", soup.get_text("one two three"))
        self.assertEqual("one two three", soup.get_text("one two three"))




