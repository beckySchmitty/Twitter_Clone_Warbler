"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY


db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        u1 = User.signup("test_user", "test@test.com", "password", None)
        u1_id = 111
        u1.id = u1_id

        db.session.commit()

        self.u1 = u1

        # u2 = User.signup("test_user_two", "test2@test.com", "password", None)
        # u2_id = 222
        # u2.id = u2_id

        # db.session.add_all([u1, u2])
        # db.session.commit()

        # u1 = User.query.get(u1_id)
        # u2 = User.query.get(u2_id)

        # self.u1 = u1
        # self.u2 = u2

        # self.client = app.test_client()

    def test_add_message(self):
        """Can use add a message?"""

        with self.client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.u1.id

        resp = self.client.post("/messages/new", data={"text": "Hello"})

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, 'http://localhost/users/111')

        msg = Message.query.one()
        self.assertEqual(msg.text, "Hello")


    def test_message_delete(self):
        with self.client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.u1.id
        
        msg = Message(text="testing message content", user_id=111)
        msg.id = 1234
        db.session.add(msg)
        db.session.commit()

        resp = self.client.post("/messages/1234/delete", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        msg_d = Message.query.get(1234)
        self.assertIsNone(msg_d)
