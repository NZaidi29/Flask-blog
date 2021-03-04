from flask import render_template, url_for, request, redirect, flash
from blog import app, db
from blog.models import User, Post, Comment
from blog.forms import RegistrationForm, LoginForm, CommentForm, SortForm, SearchForm
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')

@app.route("/home")#home page
def home():
    search = SearchForm()
    featured = Post.query.filter(Post.tag == 'featured')
    return render_template('home.html', featured=featured, search=search)

@app.route("/about")#about page
def about():
    search = SearchForm()
    return render_template('about.html', title='About Us', search=search)

@app.route("/post/<int:post_id>")#page displaying a singlar post
def post(post_id):
    search = SearchForm()
    post = Post.query.get_or_404(post_id)
    paragraphs = post.content.split("#")
    comments = Comment.query.filter(Comment.post_id == post.id)
    form = CommentForm()
    return render_template('post.html', title=post.title, post=post, comments=comments, form=form, search=search, paragraphs=paragraphs)

@app.route("/allposts", methods=['GET', 'POST'])# all posts
def allposts():
    search = SearchForm()
    form = SortForm()
    if form.validate_on_submit():
        if form.sorting.data == 'Newest':
            posts = Post.query.order_by(Post.date.desc()).all()
            return render_template('allposts.html', form= form, posts=posts, search=search)
        elif form.sorting.data == 'Oldest':
            posts = Post.query.order_by(Post.date.asc()).all()
            return render_template('allposts.html', form= form, posts=posts, search=search)
        else:
            posts = Post.query.all()
            return render_template('allposts.html', form= form, posts=posts, search=search)
    posts = Post.query.all()
    return render_template('allposts.html', form= form, posts=posts, search=search)

@app.route("/register", methods=['GET', 'POST'])#registration page
def register():
    search = SearchForm()
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(firstname=form.firstname.data, lastname=form.lastname.data, username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful.')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form, search=search)

@app.route("/login", methods=['GET', 'POST'])#login page
def login():
    search = SearchForm()
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            flash('Login successful.')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.')
    return render_template('login.html', title='Login', form=form, search=search)

@app.route("/logout")#and we logging out bois
def logout():
    search = SearchForm()
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('home'))

@app.route('/post/<int:post_id>/comment', methods=['GET', 'POST'])#adding comments to posts
@login_required
def post_comment(post_id):
    search = SearchForm()
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        db.session.add(Comment(content=form.comment.data, post_id=post.id, author_id=current_user.id))
        db.session.commit()
        flash("Your comment has been added to the post")
        return redirect(f'/post/{post.id}')
    comments = Comment.query.filter(Comment.post_id == post.id)
    return render_template('post.html', post=post, comments=comments, form=form, search=search)

@app.route('/post/<int:post_id>/favourite')#adding a post to your favourites
@login_required
def favourite(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user in post.followers:
        post.followers.remove(current_user)
        db.session.commit()
        flash("Post has been removed from favourites.")
    else:
        post.followers.append(current_user)
        db.session.commit()
        flash("Post has been added to favourites.")
    return redirect(f'/post/{post.id}')

@app.route('/post/<int:post_id>/like')#adding a post to your favourites
@login_required
def like(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user in post.likers:
        post.likers.remove(current_user)
        db.session.commit()
        flash("You have unliked this post.")
    else:
        post.likers.append(current_user)
        db.session.commit()
        flash("You have liked this post.")
    return redirect(f'/post/{post.id}')

@app.route("/profile/<username>")#adding a user profile for each user
@login_required
def profile(username):
    search = SearchForm()
    posts = current_user.favourites
    comments = Comment.query.filter(Comment.author_id == current_user.id)
    return render_template('profile.html', comments=comments, posts=posts, search=search)

@app.route('/profile/<username>/post<int:post_id>/unfavourite')#adding a post to your favourites
@login_required
def unfavourite(post_id, username):
    search = SearchForm()
    post = Post.query.get_or_404(post_id)
    if current_user in post.followers:
        post.followers.remove(current_user)
        db.session.commit()
        flash("Post has been removed from favourites.")
    posts = current_user.favourites
    comments = Comment.query.filter(Comment.author_id == current_user.id)
    return render_template('profile.html', comments=comments, posts=posts, search=search)

@app.route("/search", methods=['GET', 'POST'])
def search():
    search = SearchForm()
    if search.validate_on_submit():
        # reference for how to input the data into the like statement
        # accessed on 15/02/2021
        # https://stackoverflow.com/questions/3325467/sqlalchemy-equivalent-to-sql-like-statement
        query = "%{}%".format(search.query.data)
        # refernce for filtering multiple columns
        # accessed on 15/02/2021
        # https://stackoverflow.com/questions/3332991/sqlalchemy-filter-multiple-columns
        posts = Post.query.filter(db.or_(Post.title.like(query), Post.content.like(query)))
        return render_template('search.html', posts=posts, search=search)
    else:
        flash("I am afraid your search failed as it must contain letters or numbers without trailing spaces. Please try again.")
        return redirect(f'/allposts')
