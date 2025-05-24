import os
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

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
    image = db.Column(db.String(120), unique=True, nullable=False) # string is the url to the image 
    makeup_list_id = db.Column(db.Integer, nullable=False) 
    post_id = db.Column(db.Integer, primary_key=True)


    # foreign key to user 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



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

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    
    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
