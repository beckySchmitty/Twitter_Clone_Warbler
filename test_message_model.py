"""Message model tests."""

import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes


os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()


class MessageModelTestCase(TestCase):
    """Test model for Message."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.u_id = 111
        u = User.signup("test_user", "testing@test.com", "password", None)
        u.id = self.u_id
        db.session.commit()

        self.u = User.query.get(self.u_id)

        # to prevent detached SQLAlchemy issue later
        self.u_likes = self.u.likes

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does basic model work?"""
        
        m = Message(
            text="random warble",
            user_id=self.u_id
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
        u2_id = 222
        u2.id = u2_id
        db.session.add(u2)
        db.session.commit()

        
        m1 = Message(
            text="warble warble",
            user_id=self.u_id
        )
        m2 = Message(
            text="wareble not created by self.u",
            user_id=u2_id
        )

        db.session.add_all([m1, m2])
        db.session.commit()

        self.u_likes.append(m2)

        db.session.commit()

        self.assertEqual(self.u_likes[0].text, "wareble not created by self.u")