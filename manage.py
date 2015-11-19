import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
import os
from app import create_app,db
from app.models import User,Role,Permission,Post
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate,MigrateCommand


app = create_app('default')
manager = Manager(app)
migrate = Migrate(app,db)

@manager.command
def test():
	"""Run test unit tests"""
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)

def make_shell_context():
	return dict(app=app,User=User,Role=Role,db=db,Permission=Permission,Post=Post)
manager.add_command('shell',Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)



if __name__ == '__main__':
	manager.run()
