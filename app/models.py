import hashlib
from datetime import datetime
from markdown import markdown
import bleach
from . import db,login_manager
from flask.ext.login import UserMixin,AnonymousUserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask import current_app,request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class Permission:
	FOLLOW = 0x01
	COMMENT = 0x02
	WRITE_ARTICLES = 0x04
	MODERATE_COMMENTS = 0x08
	ADMINISTER = 0x80

class Follow(db.Model):
	__tablename__="follows"
	follower_id = db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
	followed_id = db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
	timestamp = db.Column(db.DateTime,default=datetime.utcnow)

class User(db.Model,UserMixin):
	__tablename__ = 'users'

	id = db.Column(db.Integer,primary_key=True)
	email = db.Column(db.String(64),unique=True,index=True)
	username = db.Column(db.String(64),unique=True,index=True)
	password_hash = db.Column(db.String(128))
	role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
	confirmed = db.Column(db.Boolean,default=False)
	name = db.Column(db.String(64))
	location = db.Column(db.String(64))
	about_me=db.Column(db.Text())
	member_since = db.Column(db.DateTime(),default=datetime.utcnow)
	last_seen = db.Column(db.DateTime(),default = datetime.utcnow)
	avatar_hash = db.Column(db.String(32))
	posts = db.relationship('Post',backref='author',lazy='dynamic')
	followed= db.relationship('Follow',foreign_keys=[Follow.follower_id],
		backref=db.backref('follower',lazy='joined'),lazy='dynamic',
		cascade='all,delete-orphan')
	followers = db.relationship('Follow',foreign_keys=[Follow.followed_id],
		backref=db.backref('followed',lazy='joined'),lazy='dynamic',
		cascade='all,delete-orphan')


	def __init__(self,**kwargs):
		super(User,self).__init__(**kwargs)
		if self.role is None:
			if self.email == 'luna825@qq.com':
				self.role = Role.query.filter_by(permission = 0xff).first()
			else:
				self.role = Role.query.filter_by(default=True).first()
		if self.email is not None and self.avatar_hash is None:
			self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
		self.followed.append(Follow(followed=self))

	@staticmethod
	def generate_fake(count=100):
		from sqlalchemy.exc import IntegrityError
		from random import seed
		import forgery_py

		seed()
		for i in range(count):
			u = User(email=forgery_py.internet.email_address(),
				username = forgery_py.internet.user_name(True),
				password = forgery_py.lorem_ipsum.word(),
				confirmed=True,
				name = forgery_py.name.full_name(),
				location = forgery_py.address.city(),
				about_me = forgery_py.lorem_ipsum.sentence(),
				member_since=forgery_py.date.date(True))
			db.session.add(u)
			try:
				db.session.commit()
			except IntegrityError:
				db.session.rollback()

	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)

	#head gravatar
	def gravatar(self,size=100,default='identicon',rating='g'):
		if request.is_secure:
			url = 'https://secure.gravatar.com/avatar'
		else:
			url = 'http://gravatar.duoshuo.com/avatar'
		hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
			url=url,hash=hash,size=size,default=default,rating=rating)


	#password hash
	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')
	@password.setter
	def password(self,password):
		self.password_hash = generate_password_hash(password)
	def verify_password(self,password):
		return check_password_hash(self.password_hash,password)

	#confirmed accout
	def generate_confirmation_token(self,expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'],expiration)
		return s.dumps({'confirm':self.id})
	def confirm(self,token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('confirm') != self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		return True
	#reset password
	def generate_reset_password_token(self,expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'],expiration)
		return s.dumps({'reset':self.id})
	def reset_password(self,token,new_password):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('reset') != self.id:
			return False
		self.password = new_password
		db.session.add(self)
		return True

	#role auth
	def can(self,permission):
		return self.role is not None and (self.role.permission & permission) == permission
	def is_administrator(self):
		return self.can(Permission.ADMINISTER)

	#follow
	def is_following(self,user):
		return self.followed.filter_by(followed_id=user.id).first() is not None
	def is_followed_by(self,user):
		return self.followers.filter_by(follower_id=user.id).first() is not None
	def follow(self,user):
		if not self.is_following(user):
			f = Follow(follower=self,followed=user)
			db.session.add(f)
	def unfollow(self,user):
		f = self.followed.filter_by(followed_id = user.id).first()
		if f:
			db.session.delete(f)
	@property
	def followed_posts(self):
		return Post.query.join(Follow,Follow.followed_id == Post.auth_id)\
				.filter(Follow.follower_id==self.id)
	@staticmethod
	def add_some_follow(count=10):
		from random import seed,randint
		seed()
		users = User.query.all()
		user_count = len(users)
		for user in users:
			for i in range(count):
				u = User.query.offset(randint(0,user_count-1)).first()
				if not user.is_following(u):
					user.follow(u)
		db.session.commit()
	@staticmethod
	def add_self_follow():
		users = User.query.all()
		for u in users:
			if not u.is_following(u):
				u.follow(u)
		db.session.commit()


		
	def __repr__(self):
		return '<User %r>' % self.email

class AnonymousUser(AnonymousUserMixin):
	def can(self,permission):
		return False
	def is_administrator(self):
		return False
login_manager.anonymous_user = AnonymousUser




class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(64),unique=True,index=True)
	default = db.Column(db.Boolean,default=False,index = True)
	permission = db.Column(db.Integer)
	users = db.relationship('User',backref='role',lazy='dynamic')

	def __repr__(self):
		return '<Role %r>' % self.name

	@staticmethod
	def insert_roles():
		roles = {
			'User':(Permission.FOLLOW|Permission.COMMENT|Permission.WRITE_ARTICLES,True),
			'Moderator':(Permission.FOLLOW|
						 Permission.COMMENT|
						 Permission.WRITE_ARTICLES|
						 Permission.MODERATE_COMMENTS,False),
			'Administrator':(0xff,False)
		}

		for r in roles:
			role = Role.query.filter_by(name = r).first()
			if role is None:
				role= Role(name = r)
			role.permission = roles[r][0]
			role.default = roles[r][1]
			db.session.add(role)
		db.session.commit()

class Post(db.Model):
	__tablename__='posts'
	id = db.Column(db.Integer,primary_key=True)
	body = db.Column(db.Text())
	timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
	auth_id = db.Column(db.Integer,db.ForeignKey('users.id'))
	body_html = db.Column(db.Text)

	@staticmethod
	def on_changed_body(target,value,oldvalue,initiator):
		allowed_tags=['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
		target.body_html = bleach.linkify(bleach.clean(
        	markdown(value,output_format='html'),tags=allowed_tags,strip=True))

	@staticmethod
	def generate_fake(count=100):
		from random import seed,randint
		import forgery_py

		seed()
		user_count = User.query.count()
		for i in range(count):
			u = User.query.offset(randint(0,user_count-1)).first()
			p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1,3)),
				timestamp = forgery_py.date.date(True),
				author=u)
			db.session.add(p)
			db.session.commit()

db.event.listen(Post.body,'set',Post.on_changed_body)


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))