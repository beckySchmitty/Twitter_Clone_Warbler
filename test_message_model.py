"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    """Test model for Message."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u = User.signup("test_user", "testing@test.com", "password", None)
        u.id = 222
        db.session.commit()

        self.u = User.query.get(222)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does basic model work?"""
        
        m = Message(
            text="random warble",
            user_id=self.u.id
        )
        db.session.add(m)
        db.session.commit()
        # User should now have 1 message

        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "random warble")
        self.assertNotEqual(self.u.messages, None)

        q = Message.query.filter_by(id=1).one()
        self.assertEqual(self.u.messages[0], q)

    def test_message_likes(self):
        u2 = User.signup("user_tqo", "t@email.com", "password", None)
        db.session.add(u2)
        db.session.commit()

        
        m1 = Message(
            text="warble warble",
            user_id=self.u.id
        )
        m2 = Message(
            text="wareble not created by self.u",
            user_id=u2.id
        )

        db.session.add_all([m1, m2])
        db.session.commit()

        self.u.likes.append(m2)

        db.session.commit()

        u_likes = Likes.query.filter(Likes.user_id == self.u.id).all()
        self.assertEqual(u_likes[0].message_id, m2.id)