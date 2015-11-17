import unittest,time
from datetime import datetime
from app import db,create_app
from app.models import User,Role,Permission,AnonymousUser

class ModelTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context() 
		self.app_context.push()
		db.create_all()


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

	def test_role_and_permissions(self):
		Role.insert_roles()
		u = User(email='john@example.com',password='cat')
		self.assertTrue(u.can(Permission.FOLLOW))
		self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

	def test_anonymous_user(self):
		u = AnonymousUser()
		self.assertFalse(u.can(Permission.FOLLOW))

	def test_timestamps(self):
		u = User(password='cat')
		db.session.add(u)
		db.session.commit()
		self.assertTrue((datetime.utcnow()-u.member_since).total_seconds() < 3)
		self.assertTrue((datetime.utcnow()-u.member_since).total_seconds() < 3)

	def test_ping(self):
		u = User(password='cat')
		db.session.add(u)
		db.session.commit()
		last_seen_before = u.last_seen
		time.sleep(2)
		u.ping()
		self.assertTrue(u.last_seen>last_seen_before)

	def test_gravatar(self):
		u = User(email='john@example.com',password='cat')
		with self.app.test_request_context('/'):
			gravatar = u.gravatar()
			gravatar_256 = u.gravatar(size=256)
			gravatar_pg = u.gravatar(rating='pg')
			gravatar_retro = u.gravatar(default='retro')
		self.assertTrue('http://gravatar.duoshuo.com/avatar/' +
                        'd4c74594d841139328695756648b6bd6'in gravatar)
		self.assertTrue('s=256' in gravatar_256)
		self.assertTrue('r=pg' in gravatar_pg)
		self.assertTrue('d=retro' in gravatar_retro)

		with self.app.test_request_context('/',base_url='https://example.com'):
			gravatar_ssl = u.gravatar()
		self.assertTrue('https://secure.gravatar.com/avatar/' +
                        'd4c74594d841139328695756648b6bd6' in gravatar_ssl)

