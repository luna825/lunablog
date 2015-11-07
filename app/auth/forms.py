from flask.ext.wtf import Form
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from wtforms import ValidationError

class LoginForm(Form):
	email = StringField('Email',validators=[Required(),Email(),Length(1,64)])
	password = PasswordField('Password',validators=[Required()])
	remember_me = BooleanField('Remember me')
	submit = SubmitField('Log In')

class RegisterForm(Form):
	email = StringField('Email',validators=[Required(),Email(),Length(1,64)])
	username = StringField('Username',validators=[Required(),Length(1,64),
		Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Username must have only letter,\
			numbers,dots or underline')])
	password = PasswordField('Password',validators=[Required(),
		EqualTo('password2',message='Password must match')])
	password2 = PasswordField('Confirm Password',validators=[Required()])
	submit = SubmitField('Register')

	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already Register')