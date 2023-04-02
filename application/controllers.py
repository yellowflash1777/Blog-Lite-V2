from datetime import datetime
import os
from flask import abort, render_template, flash, redirect, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from .forms import AddPostForm, CommentForm, EditUserForm, LoginForm, RegistrationForm
from .models import Comment, Like, Post, User
from .follow import Follow
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        return render_template('index.html')
    
@app.route('/home')
@login_required
def home():
        # Get IDs of users that the current user is following
    following_ids = [followed_user.id for followed_user in current_user.following]

        # Retrieve posts made by these users, ordered by timestamp in descending order
    posts = Post.query.filter(Post.user_id.in_(following_ids)).order_by(Post.timestamp.desc()).all()

    return render_template('home.html', posts=posts)
    

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
    num_posts = Post.query.filter_by(user_id=user.id).count()
    num_followers = Follow.query.filter_by(followed_user_id=user.id).count()
    num_following = Follow.query.filter_by(follower_user_id=user.id).count()

    return render_template('profile.html', user=user, is_following=is_following, is_followed_by=is_followed_by, num_followers=num_followers, num_following=num_following, num_posts=num_posts)



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

@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = AddPostForm()
    if form.validate_on_submit():
        # Save the image file to the specified directory
        file = form.image.data
        if file:
            if file.content_length > MAX_FILE_SIZE:
                flash('File size exceeds the limit of 5MB.', 'error')
                return redirect(request.url)
            if not allowed_file(file.filename):
                flash('Invalid file type. Allowed types are png, jpg, jpeg, and gif.', 'error')
                return redirect(request.url)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename))
        else:
            filename = None
        
        timestamp = datetime.utcnow()
        post = Post(title=form.title.data, content=form.content.data, 
                    image_url=filename, user=current_user , timestamp=timestamp)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('add_post.html', title='New Post', form=form)
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/post/<int:post_id>')
def view_post(post_id):
    # Retrieve the post from the database
    post = Post.query.get_or_404(post_id)
    # Retrieve the post's comments from the database
    # comments = Comment.query.filter_by(post=post).all()
    # Retrieve the post's likes from the database
    # likes = Like.query.filter_by(post=post).all()
    form=CommentForm()
    # print(len(post.likes))
    # print(current_user.is_following(post.user))
    # Render the view_post.html template with the post, comments, and likes
    return render_template('view_post.html', post=post,form=form)

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = AddPostForm()
    if form.validate_on_submit():
        # Save the image file to the specified directory
        file = form.image.data
        if file:
            if file.content_length > MAX_FILE_SIZE:
                flash('File size exceeds the limit of 5MB.', 'error')
                return redirect(request.url)
            if not allowed_file(file.filename):
                flash('Invalid file type. Allowed types are png, jpg, jpeg, and gif.', 'error')
                return redirect(request.url)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename))
        else:
            filename = post.image_url
        
        post.title = form.title.data
        post.content = form.content.data
        post.image_url = filename
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    return render_template('edit_post.html', title='Edit Post', form=form, post=post)

@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    
    if post.user_id != current_user.id:
        print(type(post.user_id))
        print(type(current_user.id))
        abort(403) # Forbidden
    
    # Delete the image file from the file system
    if post.image_url:
        try:
            os.remove(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], post.image_url))
        except OSError:
            pass
    
    # Delete the post from the database
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('index'))



@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.is_liking(post):
        flash('You have already liked this post')
        return redirect(url_for('view_post', post_id=post.id))
    like = Like(user_id=current_user.id, post_id=post.id, timestamp=datetime.utcnow())
    db.session.add(like)
    db.session.commit()
    return redirect(url_for('view_post', post_id=post.id))

@app.route('/unlike/<int:post_id>', methods=['POST'])
@login_required
def unlike_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    if not like:
        flash('You have not liked this post')
        return redirect(url_for('view_post', post_id=post.id))
    db.session.delete(like)
    db.session.commit()
    return redirect(url_for('view_post', post_id=post.id))

@app.route('/post/<int:post_id>/comments', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            post_id=post_id,
            user_id=current_user.id,
            comment=form.comment.data,
            timestamp=datetime.utcnow()
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('view_post', post_id=post_id))
    return render_template('view_post.html', post=post, form=form)

@app.route('/post/<int:post_id>/likes')
@login_required
def post_likes(post_id):
    post = Post.query.get_or_404(post_id)
    likers = post.likes
    print(likers[0].user)
    return render_template('post_likes.html', post=post, likers=likers)

@app.route('/followers/<int:user_id>')
@login_required
def followers(user_id):
    user = User.query.get_or_404(user_id)
    followers = user.followers
    # print(followers[0].follower_user.username)
    return render_template('followers.html', user=user, followers=followers)

@app.route('/following/<int:user_id>')
@login_required
def following(user_id):
    user = User.query.get_or_404(user_id)
    following = user.following
    return render_template('following.html', user=user, following=following)

