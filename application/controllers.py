from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from .forms import LoginForm, RegistrationForm
from .models import User


@app.route('/')
@login_required
def index():
    return redirect(url_for('home'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if not form.validate_username():
            flash('Username is already taken')
            return redirect(url_for('register'))
        # Create new user
        if form.password.data != form.password2.data:
            flash('Passwords do not match')
            return redirect(url_for('register'))
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# @app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
# @login_required
# def edit_user(user_id):
#     user = User.query.get(user_id)
#     form = EditUserForm(obj=user)
#     if form.validate_on_submit():
#         form.populate_obj(user)
#         db.session.commit()
#         flash('User information has been updated')
#         return redirect(url_for('profile', user_id=user.id))
#     return render_template('edit_user.html', title='Edit User', form=form)

# @app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
# @login_required
# def delete_user(user_id):
#     user = User.query.get(user_id)
#     if user:
#         db.session.delete(user)
#         db.session.commit()
#         flash('User has been deleted')
#     else:
#         flash('User not found')
#     return redirect(url_for('home'))

@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = AddPostForm()
    if form.validate_on_submit():
        # Save image to server
        image = form.image.data
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)

        # Create new post
        post = Post(title=form.title.data, content=form.content.data, image=image_filename, author=current_user)
        db.session.add(post)
        db.session.commit()

        flash('Your post has been created!', 'success')
        return redirect(url_for('post', post_id=post.id))

    return render_template('add_post.html', title='Add Post', form=form)

