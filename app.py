import os
from flask import Flask, request, render_template, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

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
    makeup_list_id = db.Column(db.Integer, nullable=False)

    # foreign key to user table
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

class List(db.Model):
   __tablename__ = 'list'
   # foreign key to post_id
   # accesses post_id from Post
   post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), primary_key=True)
   item_name = db.Column(db.String(120), nullable=False, primary_key=True)


class Bag(db.Model):
   __tablename__ = 'bag'
   user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
   item_name = db.Column(db.String(120), db.ForeignKey('list.item_name'), unique=True, nullable=False)


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

        # Now pass user info to the template
        return render_template('home.html', username=user.username)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
