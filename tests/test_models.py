import unittest,time
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

	def test_user_confirmed(self):
		u = User(password='cat')
		db.session.add(u)
		db.session.commit()
		token = u.generate_confirmation_token()
		self.assertTrue(u.confirm(token))

		u2 = User(password = 'cat')
		db.session.add(u2)
		db.session.commit()
		self.assertFalse(u2.confirm(token))

	def test_user_confirmed_expired(self):
		u = User(password='cat')
		db.session.add(u)
		db.session.commit()
		token = u.generate_confirmation_token(1)
		time.sleep(2)
		self.assertFalse(u.confirm(token))

	def test_reset_password_token(self):
		u = User(password = 'cat')
		db.session.add(u)
		db.session.commit()
		token = u.generate_reset_password_token()
		self.assertTrue(u.reset_password(token,'dog'))
		self.assertTrue(u.verify_password('dog'))

	def test_invalid_reset_token(self):
		u1 = User(password='cat')
		u2 = User(password='dog')
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()
		token = u1.generate_reset_password_token()
		self.assertFalse(u2.reset_password(token,'horse'))
		self.assertTrue(u2.verify_password('dog'))