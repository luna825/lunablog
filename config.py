import os 

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = 'hard to guess string'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	FLASK_POSTS_PER_PAGE = 10
	FLASKY_MAIL_SUJECT_PREFIX = '[Flasky]'
	FLASKY_MAIL_SENDER = 'Flasky Admin <luna825@qq.com>'
	MAIL_SERVER = 'smtp.qq.com'
	MAIL_PORT = 465
	MAIL_USE_SSL = True
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = \
			'sqlite:///' + os.path.join(basedir,'data-dev.sqlite')

class TestingConfig(Config):
	TESTING = True
	WTF_CSRF_ENABLED = False
	SQLALCHEMY_DATABASE_URI = \
			'sqlite:///' + os.path.join(basedir,'data-test.sqlite')

class ProductionCofig(Config):
	DEBUG = False
	SQLALCHEMY_DATABASE_URI = \
			'sqlite:///' + os.path.join(basedir,'data.sqlite')

config = {
	'development':DevelopmentConfig,
	'testing':TestingConfig,
	'production':ProductionCofig,

	'default':DevelopmentConfig
}