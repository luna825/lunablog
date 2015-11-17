from flask import render_template,url_for,flash,redirect,request
from flask.ext.login import login_user,login_required,logout_user,current_user
from . import auth
from forms import LoginForm,RegisterForm,ChangePasswordForm,\
					ResetPasswordRequestForm,ResetPasswordForm
from ..models import User,Role
from ..email import send_email
from .. import db

@auth.route('/login',methods=["GET","POST"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user,form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('Invalid email or password','danger')
	return render_template('auth/login.html',form=form)

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('main.index'))

@auth.route('/register',methods=["GET","POST"])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		user = User(email=form.email.data,username=form.username.data,
			password=form.password.data)
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmation_token()
		send_email(user.email,'Confirm you accout',
			'auth/email/confirm',user=user,token=token)
		flash('A confirm email has been sent to you by email.')
		return redirect(url_for('auth.login'))
	return render_template('auth/register.html',form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for('main.index'))
	if current_user.confirm(token):
		flash('You have confirmed your account.Thanks')
	else:
		flash('The confirmation link is invalid or has expired.')
	return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		current_user.ping()
		if not current_user.confirmed and request.endpoint[:5] != 'auth.':
			return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(current_user.email,
		'Confirm you account','auth/email/confirm',user=current_user,token=token)
	flash('A new confirmation email has been sent to you by email.')
	return redirect(url_for('main.index'))

@auth.route('/change-password',methods=["GET","POST"])
@login_required
def change_password():
	form = ChangePasswordForm()
	if form.validate_on_submit():
		if current_user.verify_password(form.old_password.data):
			current_user.password = form.password.data
			db.session.add(current_user)
			flash('You password have been update','success')
			return redirect(url_for('main.index'))
		else:
			flash('Invalid password')
	return render_template('auth/change_password.html',form = form)

@auth.route('/reset',methods=["GET","POST"])
def reset_password_request():
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = ResetPasswordRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			token = user.generate_reset_password_token()
			send_email(user.email,'Reset Password',
				'auth/email/reset_password',user=user,token=token,
				next=request.args.get('next'))
			flash('An email with instructions to reset your password has been '
				'sent ot you.')
			return redirect(url_for('auth.login'))
	return render_template('auth/reset_password.html',form = form)

@auth.route('/reset/<token>',methods=["GET","POST"])
def reset_password(token):
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is None:
			return redirect(url_for('main.index'))
		if user.reset_password(token,form.password.data):
			flash('You password have been update')
			return redirect(url_for('auth.login'))
		else:
			return redirect(url_for('main.index'))
	return render_template('auth/reset_password.html',form = form)


