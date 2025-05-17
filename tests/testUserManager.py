import unittest
from flask import Flask
from werkzeug.security import generate_password_hash
from python_gyak.models import db, User, UserManager

class TestUserManager(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SECRET_KEY'] = 'secret'
        db.init_app(self.app)
        self.app.app_context().push()

        with self.app.app_context():
            db.create_all()

        db.session.add(User(username="admin", email="admin@admin.admin", password=generate_password_hash("admin")))
        db.session.commit()

        self.userManager = UserManager()

    def test_register(self):
        self.assertEqual(self.userManager.register("valaki", " ", "pw"), "Adj meg minden adatot!")
        self.assertEqual(self.userManager.register("admin", "user@email.hu", "pw"), "A felhasználónév foglalt.")
        self.assertEqual(self.userManager.register("test_user", "admin@admin.admin", "pw"), "Az email cím már foglalt.")
        self.assertEqual(self.userManager.register("test_user", "test@email.hu", "pw"), "")

    def test_login(self):
        with self.app.test_request_context():
            self.assertEqual(self.userManager.login("admin", "asd"), "Hibás felhasználónév vagy jelszó")
            self.assertEqual(self.userManager.login("asd", "admin"), "Hibás felhasználónév vagy jelszó")
            self.assertEqual(self.userManager.login("admin", "admin"), "Sikeres bejelentkezés")

    def test_get_user(self):
        with self.app.test_request_context():
            self.userManager.login("admin", "admin")
            self.assertEqual(self.userManager.get_user()['username'], "admin")
            self.assertEqual(self.userManager.get_user()['email'], "admin@admin.admin")

            self.userManager.logout()
            self.assertEqual(self.userManager.get_user()['username'], None)
            self.assertEqual(self.userManager.get_user()['email'], None)