import unittest
from flask import Flask
from python_gyak.models import WatchedManager, db, Watched

class TestWatchedManager(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SECRET_KEY'] = 'secret'
        db.init_app(self.app)
        self.app.app_context().push()

        with self.app.app_context():
            db.create_all()

        db.session.add(Watched(username="admin", id=1))
        db.session.add(Watched(username="admin", id=2))
        db.session.add(Watched(username="admin", id=3))
        db.session.commit()

        self.manager = WatchedManager()

    def test_get_all(self):
        episodes = self.manager.get_all("admin")
        self.assertIsInstance(episodes, list)
        self.assertEqual(len(episodes), 3)

    def test_stats(self):
        stats = self.manager.stats("admin")
        self.assertIsInstance(stats, dict)
        self.assertEqual(len(stats), 3)
        self.assertEqual(stats["episodes"], 3)
        self.assertEqual(stats["shows"], 1)
