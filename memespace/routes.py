
from flask import render_template, url_for, flash, redirect, request
from memespace import app, db, bcrypt
from memespace.forms import RegistrationForm, LoginForm, UpdateAccountForm, MemeForm
from memespace.models import User, MemeDatabase
from flask_login import login_user, current_user, logout_user, login_required

NO_OF_MEMES = 2
CURRENT = 1
posts = [
    {
        'author': 'Atharva Chincholkar',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20,2019'
    },
    {
        'author': 'Bob C',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21,2019'
    }
]
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    global CURRENT
    CURRENT = 1
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            #memespace
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login failed', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    global CURRENT
    CURRENT = 1
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


def incCurrent():
    global CURRENT
    global NO_OF_MEMES
    if CURRENT < NO_OF_MEMES:
        CURRENT+=1
    return CURRENT

@app.route("/round1", methods=['GET', 'POST'])
@login_required
def round1():
    global CURRENT
    filenames = [f'id{x}' for x in range(1,NO_OF_MEMES+1)]
    meme_images = [url_for('static', filename='memes/'+ x + '.jpg') for x in filenames]
    form = MemeForm()
    if form.validate_on_submit():
        resp = MemeDatabase(image_id=str(CURRENT), content1=form.content1.data, content2=form.content2.data, author=current_user)
        db.session.add(resp)
        db.session.commit()
        flash('Response Recorded')
        if CURRENT < NO_OF_MEMES:
            CURRENT += 1
            return render_template('round1.html', title='Round 1', meme_images=meme_images[CURRENT-1], form=form)
        else:
            CURRENT = 0
            return redirect(url_for('account'))

    return render_template('round1.html', title='Round 1', meme_images=meme_images[CURRENT-1], form=form)
