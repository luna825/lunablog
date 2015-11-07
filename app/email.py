from threading import Thread
from . import mail
from flask.ext.mail import Message
from flask import current_app,render_template

def send_async_email(app,msg):
	with app.app_context():
		mail.send(msg)

def send_email(to,subject,template,**kwargs):
	app = current_app._get_current_object()
	msg = Message(app.config['FLASKY_MAIL_SUJECT_PREFIX']+ ' ' + subject,
		sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
	msg.body = render_template(template+'.txt',**kwargs)
	msg.html = render_template(template+'.html',**kwargs)
	thr = Thread(target=send_async_email,args=[app,msg])
	thr.start()
	return thr