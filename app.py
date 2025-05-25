import os
from flask import Flask, request, render_template, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from makeup import get_makeup_data, search_by_param

app = Flask(__name__)
app.secret_key = 'secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# set up virtual environment 

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)


    # user can have multiple posts
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    __tablename__ = 'post'
    post_id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(120), unique=True, nullable=False)
    makeup_list_id = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(80), nullable=True)

    # foreign key to user table
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

class List(db.Model):
   __tablename__ = 'list'
   # foreign key to post_id
   # accesses post_id from Post
   post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), primary_key=True)
   item_name = db.Column(db.String(120), nullable=False, primary_key=True)


class makeup_Bag(db.Model):
   __tablename__ = 'makeup_bag'
   user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False) # connect to the user table 
   item_id = db.Column(db.Integer, unique=True, nullable=False)
   makeup_bag_id = db.Column(db.Integer, primary_key=True)
   website_url = db.Column(db.String(120), nullable=False)

def add_to_makeup_bag(user_id, item_id, website_url):
    makeup_bag_item = makeup_Bag(user_id=user_id, item_id=item_id, website_url=website_url)
    db.session.add(makeup_bag_item)
    db.session.commit()

def remove_from_makeup_bag(user_id, item_id):
    makeup_bag_item = makeup_Bag.query.filter_by(user_id=user_id, item_id=item_id).first()
    if makeup_bag_item:
        db.session.delete(makeup_bag_item)
        db.session.commit()

# create, remove, update, and delete posts
def create_post(user_id, image, post_title) :
    post = Post(user_id=user_id, image=image, title=post_title)
    db.session.add(post)
    db.session.commit()

def delete_post(user_id, post_id) :
    post = Post.query.filter_by(post_id=post_id, user_id=user_id)
    if post :
        db.session.delete(post)
        db.session.commit()

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()

        if not user:
            # Create a new user
            user = User(username=username)
            db.session.add(user)
            db.session.commit()

        # Set session variables BEFORE redirect
        session['user_id'] = user.user_id
        session['username'] = user.username

        return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/home')
def home():
    user_id = session.get('user_id')  
    if user_id:
        user = User.query.get(user_id)  # Query user by ID
        if not user:
            return redirect(url_for('login'))  # User not found, redirect to login
        
        # retrieve top 20 posts to display on the main page

        # Now pass user info to the template
        return render_template('home.html', username=user.username)
    return redirect(url_for('login'))

@app.route('/land')
def land():
    return render_template('index.html')
    


if __name__ == '__main__':
    app.run(debug=True)
