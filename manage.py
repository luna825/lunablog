import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
import os
COV = None
if os.environ.get('FLASK_COVERAGE'):
	import coverage
	COV = coverage.coverage(branch=True,include='app/*')
	COV.start()

from app import create_app,db
from app.models import User,Role,Permission,Post
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate,MigrateCommand


app = create_app('default')
manager = Manager(app)
migrate = Migrate(app,db)

@manager.command
def test(coverage=False):
	"""Run test unit tests"""
	if coverage and not os.environ.get('FLASK_COVERAGE'):
		import sys
		os.environ['FLASK_COVERAGE'] = '1'
		os.execvp(sys.executable,[sys.executable]+sys.argv)
	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)
	if COV:
		COV.stop()
		COV.save()
		print('Coverage summary:')
		COV.report()
		basedir = os.path.abspath(os.path.dirname(__file__))
		covdir = os.path.join(basedir,'tmp/coverage')
		COV.html_report(directory = covdir)
		print('HTML version: file://%s/index.html' % covdir)
		COV.erase()

def make_shell_context():
	return dict(app=app,User=User,Role=Role,db=db,Permission=Permission,Post=Post)
manager.add_command('shell',Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)



if __name__ == '__main__':
	manager.run()
