import os
from flask import Flask, jsonify, request, render_template, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from makeup import get_makeup_data, search_by_param

app = Flask(__name__)
app.secret_key = 'secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# table creation
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
    post_title = db.Column(db.String(80), nullable=True)

    # foreign key to user table
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

class List(db.Model):
   __tablename__ = 'list'
   # foreign key to post_id
   # accesses post_id from Post
   post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'), primary_key=True)
   item_name = db.Column(db.String(120), nullable=False, primary_key=True)

class all_Products(db.Model):
    __tablename__ = 'all_products'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    brand = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float)
    image_url = db.Column(db.String(120), nullable=False)
    product_url = db.Column(db.String(120), nullable=False)

class bag_item(db.Model):
    __tablename__ = 'bag_item'
    bag_item_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('all_products.product_id'), unique=True, nullable=False)  # connect to the all_products table
    item_name = db.Column(db.String(120), db.ForeignKey('all_products.name'), nullable=False)  
    makeup_bag_id = db.Column(db.Integer, db.ForeignKey('makeup_bag.makeup_bag_id'))
    website_url = db.Column(db.String(120), db.ForeignKey('all_products.product_url'), nullable=False)
    image_url = db.Column(db.String(120), db.ForeignKey('all_products.image_url'), nullable=False)

    makeup_bag = db.relationship('makeup_Bag', back_populates='items')

class makeup_Bag(db.Model):
   __tablename__ = 'makeup_bag'
   user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False, unique=True) # connect to the user table 
   makeup_bag_id = db.Column(db.Integer, primary_key=True)

   items = db.relationship('bag_item', back_populates='makeup_bag', cascade='all, delete-orphan') #bag can have mutiple items
    

def load_product_table(): # function to load makeup table into the database so we can use it later 
    if all_Products.query.first() is not None: # if the table is already loaded, do not load again
        return
    makeup_data = get_makeup_data()
    if makeup_data:
        for product in makeup_data:
            name = product.get("name")
            brand = product.get("brand")
            price = product.get("price")
            image_url = product.get("image_link")
            product_url = product.get("product_link")

            if not (name and brand and price and product_url):
                continue

            new_product = all_Products(
                name=name,
                brand=brand,
                price=price,
                image_url=image_url,
                product_url=product_url,
            )
            db.session.add(new_product)

        db.session.commit()

# create, remove, update, and delete posts
def create_post(user_id, image, post_title) :
    post = Post(user_id=user_id, image=image, post_title=post_title)
    db.session.add(post)
    db.session.commit()

def delete_post(user_id, post_id) :
    post = Post.query.filter_by(post_id=post_id, user_id=user_id)
    if post :
        db.session.delete(post)
        db.session.commit()

with app.app_context():
    #db.drop_all() # do once and then delete to reset tables
    db.create_all()
    load_product_table()  # Load makeup data into the database

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': # get user or create user depending on input 
        username = request.form['username']
        user = User.query.filter_by(username=username).first()

        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()

        session['user_id'] = user.user_id
        session['username'] = user.username

        return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/home')
def home():
    user_id = session.get('user_id')  
    if user_id:
        user = User.query.get(user_id)  
        if not user:
            return redirect(url_for('login'))  
        
        # retrieve top 20 posts to display on the main page
        posts = Post.query.limit(20).all()

        # Now pass user info to the template
        return render_template('home.html', username=user.username, posts=posts)
    return redirect(url_for('login'))

@app.route('/makeup_bag', methods=['GET']) # this allows user to search for products and view their bag
def makeup_bag():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    query = request.args.get('q', '')
    products = []
    if query:
        products = all_Products.query.filter(
            (all_Products.name.ilike(f'%{query}%')) |
            (all_Products.brand.ilike(f'%{query}%'))
        ).all()

    bag = makeup_Bag.query.filter_by(user_id=user_id).first() # find the bag, if they don't have one, create it 
    if not bag: 
        bag = makeup_Bag(user_id=user_id)
        db.session.add(bag)
        db.session.commit()

    user_items = bag.items

    return render_template(
        'makeup_bag.html',
        username=session.get('username'),
        products=products,
        items=user_items,
        query=query
    )

@app.route('/add_to_bag', methods=['POST']) # this allows user to add items to their bag 
def add_to_makeup_bag():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    item_id = request.form['item_id']
    item_name = request.form['item_name']
    website_url = request.form['website_url']
    image_url = request.form['image_url']
    query = request.form.get('query', '')  # Preserve query if coming from search

    try:
        bag = makeup_Bag.query.filter_by(user_id=user_id).first()
        if not bag:
            bag = makeup_Bag(user_id=user_id)
            db.session.add(bag)
            db.session.commit()
        
        new_item = bag_item(makeup_bag_id = bag.makeup_bag_id, item_id=item_id, item_name=item_name, website_url=website_url, image_url=image_url)
        db.session.add(new_item)
        db.session.commit()
    except Exception as e:
        print("There was an error adding the item to the bag.")

    return redirect(url_for('makeup_bag', q=query) if query else url_for('makeup_bag'))


@app.route('/remove_from_bag/<int:bag_item_id>', methods=['POST']) #allow user to remove items from their bag
def remove_from_makeup_bag(bag_item_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    bag = makeup_Bag.query.filter_by(user_id=user_id).first()
    if not bag:
        return redirect(url_for('makeup_bag'))
    
    item_to_remove = bag_item.query.filter_by(bag_item_id=bag_item_id, makeup_bag_id=bag.makeup_bag_id).first()

    if item_to_remove:
        db.session.delete(item_to_remove)
        db.session.commit()

    return redirect(url_for('makeup_bag'))

@app.route('/logout') # user can logout 
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/land')
def land():
    return render_template('index.html')

@app.route('/look/<int:post_id>', methods=['GET']) # allow user to view a specific look
def look(post_id) :
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    post = Post.query.filter_by(post_id=post_id).first()
    return redirect(url_for('specificLook'))

# for adding fake posts
@app.route('/test', methods=['POST']) # CREATE
def add_user():
    name = request.form['title']
    image = request.form['image']
    user = session.get('user_id')
    create_post(user, image, name)
    return redirect(url_for('home'))
    
if __name__ == '__main__':
    app.run(debug=True)
