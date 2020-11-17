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
    """Test views for User."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

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

    def test_user_model(self):
        """Does basic model work?"""

        rep = f"<User #{self.u1.id}: {self.u1.username}, {self.u1.email}>"
        self.assertEqual(len(self.u1.messages), 0)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(self.u1.__repr__(), rep)

# *************************************************************************** FOLLOWS TESTS
    def test_user_follows(self):
        self.u1.following.append(self.u2)
        db.session.commit() 

        self.assertEqual(self.u2.followers[0].username, self.u1.username)
        self.assertIn(self.u1, self.u2.followers)
        self.assertEqual(self.u1.following[0], self.u2)

    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit() 

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))
    
    def test_is_followed_by(self):
        self.u1.following.append(self.u2)
        db.session.commit() 

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

# *************************************************************************** SIGNUP TEST

    def test_signup(self):
        fake_signup = User.signup(
            username="FakeUser",
            email="FakeEmail@fakeemail.com",
            password="password",
            image_url="#",
        )

        db.session.commit()

        self.assertEqual(fake_signup.username, "FakeUser")
        self.assertEqual(fake_signup.email, "FakeEmail@fakeemail.com")
        self.assertNotEqual(fake_signup.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(fake_signup.password.startswith("$2b$"))

    def test_invalid_signup(self):
            with self.assertRaises(TypeError) as te:
                invalid_signup = User.signup(
                    password="HASHED_PWD",
                    image_url="#",
                )
                db.session.commit()

                the_exception = te.exception
                self.assertEqual(the_exception, "signup() missing 2 required positional arguments: 'username' and 'email'")

            with self.assertRaises(ValueError) as context:
                User.signup("testtest", "email@email.com", None, None)

# *************************************************************************** AUTHENTICATE 

    def test_auth_returns_user(self):

        self.assertTrue(User.authenticate("test_user_one", "password"))
        self.assertFalse(User.authenticate("test_user_one", "wrongpassword"))
        self.assertFalse(User.authenticate("wrong_username", "password"))
