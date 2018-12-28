import uuid
from datetime import datetime, timedelta
from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_mail import Message
from flaskblog import db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, ForgotForm, ResetpwForm
from flaskblog.models import User, Pwreset
from flaskblog.users.utils import save_picture

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect((url_for('main.home')))
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to login', 'success')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect((url_for('main.home')))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                flash('logged in Successfully!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Register', form=form)


@users.route('/logout')
def logout():
    logout_user()
    flash('Logged out Successfully!', 'success')
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if request.method == 'POST':
        if form.validate():
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('users.account'))
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


def sendmailfunction(user):
    uid = uuid.uuid4()
    res = Pwreset(reset_key=uid.hex, user_id=user.id)
    db.session.add(res)
    db.session.commit()
    # email message part
    msg = Message("Are you trying to reset your password? Here's how", sender='mailclient420@gmail.com', recipients=[user.email])
    msg.body = "Please click on the URL below to reset your password:" + " URL here: " + (request.url.split('/forgot')[0]) + "/resetpw/" + uid.hex
    mail.send(msg)


@users.route('/forgot', methods=['GET', 'POST'])
def forgot():
    form = ForgotForm()
    nowminusone = datetime.now() - timedelta(days=1)
    if request.method == 'POST':
        if form.validate():
            user = User.query.filter_by(email=form.email.data).first()
            if not user:
                flash('No data found for this email', 'danger')
            elif user:
                res = Pwreset.query.filter_by(user_id=user.id).filter_by(has_activated=False).first()
                if not res:
                    sendmailfunction(user)
                    flash('Password reset link sent to your email !!!', 'success')
                elif res:
                    if res.datetime < nowminusone:
                        db.session.delete(res)
                        db.session.commit()
                        flash('Link already sent and has expired!!! Please generate a new one', 'danger')
                    else:
                        flash('Link already sent to your email', 'warning')
    return render_template('forgot.html', title='Forgot Password', form=form)


@users.route('/resetpw/<string:token>', methods=['GET', 'POST'])
def resetpw(token):
    form = ResetpwForm()
    nowminusone = datetime.now() - timedelta(days=1)
    res = Pwreset.query.filter_by(reset_key=token).first()
    if not res:
        flash('No reset link generated!!! Please generate one.', 'danger')
        return redirect(url_for('users.forgot'))
    else:
        if res.has_activated:
            flash('Link already used once!!! Please generate a new one.', 'danger')
            return redirect(url_for('users.forgot'))
        elif not res.has_activated:
            if res.datetime < nowminusone:
                db.session.delete(res)
                db.session.commit()
                flash('Link has been expired!!! Please request for a new reset link.', 'danger')
                return redirect(url_for('users.forgot'))
            # else:
                # user = User.query.filter_by(email=res.user.email).first_or_404()
    if request.method == 'POST':
        if form.validate():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User.query.filter_by(email=res.user.email).first_or_404()
            user.password = hashed_password
            res.has_activated = True
            db.session.commit()
            flash('Your password has been updated! You are now able to login', 'success')
            return redirect(url_for('users.login'))
    return render_template('resetpw.html', title='Change Password', form=form)
