import unittest
from app import db,create_app
from app.models import User,Role

class ModelTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context() 
		self.app_context.push()
		db.create_all()
		self.client = self.app.test_client(use_cookies = True)


	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_user_password(self):
		u = User(password='cat')
		self.assertTrue(u.password_hash is not None)

		with self.assertRaises(AttributeError):
			u.password

		self.assertTrue(u.verify_password('cat'))
		self.assertFalse(u.verify_password('dog'))
		#test salts are random
		u1 = User(password='cat')
		self.assertTrue(u.password_hash != u1.password_hash)