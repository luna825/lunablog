from flask.ext.wtf import Form
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField,SelectField
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User,Role

class EditProfileForm(Form):
	name = StringField('Real name',validators=[Length(0,64)])
	location = StringField('Location',validators=[Length(0,64)])
	about_me = TextAreaField('About me')
	submit = SubmitField('Submit')

class EditProfileAdminForm(Form):
	email = StringField('Email',validators=[Required(),Email(),Length(1,64)])
	username = StringField('Username',validators=[Required(),Length(1,64),
		Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Username must have only letter,\
			numbers,dots or underline')])
	confirmed = BooleanField('confirmed')
	role = SelectField('Role',coerce=int)
	name = StringField('Real name',validators=[Length(0,64)])
	location = StringField('Location',validators=[Length(0,64)])
	about_me = TextAreaField('About me')
	submit = SubmitField('Submit')

	def __init__(self,user,*args,**kwargs):
		super(EditProfileAdminForm,self).__init__(*args,**kwargs)
		self.role.choices = [(role.id,role.name) for role in Role.query.order_by(Role.name).all()]
		self.user = user

	def validate_email(self,field):
		if field.data != self.user.email and \
			User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')

	def validate_username(self,field):
		if field.data != self.user.username and \
			User.query.filter_by(username=field.data).first():
			raise ValidationError('Username already in use.')