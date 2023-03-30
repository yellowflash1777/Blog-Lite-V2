from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from .forms import EditUserForm, LoginForm, RegistrationForm
from .models import User
from .follow import Follow



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
        if not form.validate_username(form.username):
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

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get(user_id)
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        if form.new_password.data:
            if not user.change_password(form.old_password.data, form.new_password.data):
                flash('Old password is incorrect')
                return redirect(url_for('edit_user', user_id=user.id))
        form.populate_obj(user)
        db.session.commit()
        flash('User information has been updated')
        return redirect(url_for('profile', user_id=user.id))
    return render_template('edit_user.html', title='Edit User', form=form)

@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User has been deleted')
    else:
        flash('User not found')
    return redirect(url_for('home'))

@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('index'))
    is_following = current_user.is_authenticated and current_user.is_following(user)
    is_followed_by = current_user.is_followed_by(user)

    num_followers = Follow.query.filter_by(followed_username=user.username).count()
    num_following = Follow.query.filter_by(follower_username=user.username).count()

    return render_template('profile.html', user=user, is_following=is_following, is_followed_by=is_followed_by, num_followers=num_followers, num_following=num_following)



@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query')
    if not query:
        return render_template('search.html')

    users = User.query.filter(User.username.ilike(f'%{query}%')).all()
    return render_template('search.html', users=users)

@app.route('/follow/<user_id>', methods=['GET', 'POST'])
@login_required
def follow(user_id):
    user_to_follow = User.query.filter_by(id=user_id).first()
    if not user_to_follow:
        flash(f'User "{user_to_follow.username}" not found', 'error')
        return redirect(url_for('index'))
    if current_user.is_following(user_to_follow):
        flash(f'You are already following {user_to_follow.username}', 'info')
        return redirect(url_for('profile', user_id=user_to_follow.id))
    current_user.follow(user_to_follow)
    flash(f'You are now following {user_to_follow.username}', 'success')
    return redirect(url_for('profile', user_id=user_to_follow.id))

@app.route('/unfollow/<user_id>', methods=['GET', 'POST'])
@login_required
def unfollow(user_id):
    user_to_unfollow = User.query.filter_by(id=user_id).first()
    if not user_to_unfollow:
        flash(f'User "{user_to_unfollow.username}" not found', 'error')
        return redirect(url_for('index'))
    if not current_user.is_following(user_to_unfollow):
        flash(f'You are not following {user_to_unfollow.username}', 'info')
        return redirect(url_for('profile', user_id=user_to_unfollow.id))
    current_user.unfollow(user_to_unfollow)
    flash(f'You have unfollowed {user_to_unfollow.username}', 'success')
    return redirect(url_for('profile', user_id=user_to_unfollow.id))


# @app.route('/add_post', methods=['GET', 'POST'])
# @login_required
# def add_post():
#     form = AddPostForm()
#     if form.validate_on_submit():
#         # Save image to server
#         image = form.image.data
#         image_filename = secure_filename(image.filename)
#         image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
#         image.save(image_path)

#         # Create new post
#         post = Post(title=form.title.data, content=form.content.data, image=image_filename, author=current_user)
#         db.session.add(post)
#         db.session.commit()

#         flash('Your post has been created!', 'success')
#         return redirect(url_for('post', post_id=post.id))

#     return render_template('add_post.html', title='Add Post', form=form)

