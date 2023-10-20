from flask import Flask, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm, InputForm, ConfirmForm, CommentForm, SearchForm
from datetime import datetime
from random import random
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
from werkzeug.urls import url_encode
from werkzeug.utils import secure_filename
import os
import secrets
from PIL import Image

app = Flask(__name__)
bcrypt = Bcrypt()
login_mgr = LoginManager(app)
login_mgr.init_app(app)

app.config['SECRET_KEY'] = '3553557ad92a2f1ceeca154903e252ca'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
UPLOAD_FOLDER = 'static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

@login_mgr.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique=True,nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    posts = db.relationship('Post',backref='author',lazy=True)
    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.password}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String(120))
    title = db.Column(db.String(100),nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # username = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)

    def __repr__(self):
        return f"Post('{self.id}','{self.title}','{self.date_passed}','{self.content})"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template('home.html',posts=posts)

@app.route("/about")
def about():
    return "<h1>About Page</h1>"

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/contents")
def contents():
    data = [1,2,3,4,5]
    return render_template("contents.html",data=data)

@app.route("/register",methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        flash(f'You already logged in!','success')
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!','success')
        return redirect(url_for('home'))
    return render_template("register.html",title='register',form=form)

@app.route("/login",methods=['GET','POST'])
def login():
   if current_user.is_authenticated:
        flash(f'You already logged in!','success')
        return redirect(url_for('home'))
   form = LoginForm()
   if form.validate_on_submit():
       user = User.query.filter_by(email=form.email.data).first()
       if user.password == form.password.data:
            un = user.username
            flash(f'UserID: {un}')
            login_user(user, remember=form.remeber.data)
            return redirect(url_for("home"))
   return render_template("login.html",title="login",form=form)

@app.route("/search",methods=['GET','POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        target = form.searched.data
        search_type = form.search_type.data
        if search_type=="Contents":
            posts = Post.query.filter(Post.content.like("%" + target + "%")).order_by(Post.date_posted).all()
        elif search_type=="Author":
            posts = Post.query.filter(Post.user_id.like("%" + target + "%")).order_by(Post.date_posted).all()
        else:
            posts = Post.query.filter(Post.title.like("%" + target + "%")).order_by(Post.date_posted).all()
        return render_template("search.html",title='Search',posts=posts,form=form)
    return render_template("search.html",title='Search',form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@app.route("/new",methods=["GET","POST"])
def new_post():
    form = InputForm()
    if form.validate_on_submit():
        file = "static/img/default_post_image.png"
        if form.img.data:
            file = save_picture(form.img.data)
        post = Post(user_id=current_user.id,img=file,content=form.text.data, title=form.title.data)
        db.session.add(post)
        db.session.commit()
        flash(f'Image: {file}')
        return redirect(url_for("home"))
    return render_template("newpost.html",title="New Post", form=form)

@app.route("/<int:id>/update",methods=["GET","POST"])
def update(id):
    form = InputForm()
    post = Post.query.filter_by(id=id).first()
    if form.validate_on_submit():
        if post:
            db.session.delete(post)
            db.session.commit()
            post = Post(user_id=123, id=id, content=form.text.data, title=form.title.data)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for("home"))
    return render_template("update.html",title="Update",form=form)

@app.route("/<int:id>/delete",methods=["GET","POST"])
def delete(id):
    form = ConfirmForm()
    post = Post.query.filter_by(id=id).first()
    if form.validate_on_submit():
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("delete.html",title="delete",form=form)

@app.route("/<int:id>/post",methods=["GET","POST"])
def post(id):
    post = Post.query.filter_by(id=id).first()
    form = CommentForm()
    # get all comments associated with this post
    comments = Comment.query.filter_by(post_id=id).all()
    if form.validate_on_submit():
        # create new comment object and add to database
        comment = Comment(user_id=current_user.id,content=form.comment.data,post_id=id)
        db.session.add(comment)
        db.session.commit()
        flash(f'Comment: {form.comment.data}; Post ID: {comment.post_id} ')
        return redirect(url_for('home'))
    return render_template("post.html",post=post,form=form,comments=comments)

@app.route("/logout")
def logout():
    logout_user()
    flash(f'You have logged out successfully!','success')
    return redirect(url_for("home"))

@app.route("/<int:id>/account",methods=["GET"])
def account(id):
    # get all posts associated withb this account
    posts = Post.query.filter_by(user_id=id).all()
    # get all comments associated with this account
    comments = Comment.query.filter_by(user_id=id).all()
    return render_template("account.html",title="Account",comments=comments,posts=posts)

with app.app_context():
    # db.drop_all()
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)


