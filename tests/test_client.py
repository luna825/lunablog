import unittest
from app import create_app,db
from app.models import User,Role
from flask import url_for
import re

class FlaskClientTestCase(unittest.TestCase):
	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context() 
		self.app_context.push()
		db.create_all()
		Role.insert_roles()
		self.client = self.app.test_client(use_cookies = True)


	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_home_page(self):
		response = self.client.get(url_for('main.index'))
		self.assertTrue('Stanger' in response.get_data(as_text=True))

	def test_register_login_profile_logout(self):
		response = self.client.post(url_for('auth.register'),data={
			'email':'john@example.com',
			'username':'john',
			'password':'cat',
			'password2':'cat'
			})
		self.assertTrue(response.status_code==302)

		response = self.client.post(url_for('auth.login'),data={
			'email':'john@example.com',
			'password':'cat'
			},follow_redirects=True)
		data = response.get_data(as_text=True)
		self.assertTrue(re.search('Hello,\s+john',data))

		user = User.query.filter_by(username='john').first()
		token = user.generate_confirmation_token()
		response = self.client.get(url_for('auth.confirm',token=token),
			follow_redirects=True)
		data = response.get_data(as_text=True)
		self.assertTrue('You have confirmed your account.Thanks' in data)


		response = self.client.post(url_for('auth.change_password'),data={
			'old_password':'cat',
			'password':'dog',
			'password2':'dog'
			},follow_redirects=True)
		data = response.get_data(as_text=True)
		self.assertTrue('You password have been update' in data )

		user = User.query.filter_by(username='john').first()
		self.assertTrue(user.verify_password('dog'))

		response = self.client.get(url_for('main.user',username = user.username),follow_redirects=True)
		data = response.get_data(as_text=True)
		self.assertTrue('Member since' in data)

		response = self.client.get(url_for('auth.logout'),follow_redirects=True)
		data = response.get_data(as_text=True)
		self.assertTrue('You have been logged out.' in data)