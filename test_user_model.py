"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User(email="test@test.com",
            username="test_user_one",
            password="HASHED_PASSWORD")
        u1_id = 111
        u1.id = u1_id

        u2 = User(
            email="test2@test.com",
            username="test_user_two",
            password="HASHED_PASSWORD")
        u2_id = 222
        u2.id = u2_id

        db.session.add_all([u1, u2])
        db.session.commit()

        u1 = User.query.get(u1_id)
        u2 = User.query.get(u2_id)

        self.u1 = u1
        self.u1_id = u1_id

        self.u2 = u2
        self.u2_id = u2_id

        self.client = app.test_client()


        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        self.assertEqual(len(self.u1.messages), 0)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(self.u1.__repr__(), repr)

    def test_is_following(self):
        """Does is_following show users they follow?"""
        self.u1.following.append(self.u2)
        self.assertEqual(self.u2.followers, 1)
        self.assertIn(self.u1, self.u2.followers)