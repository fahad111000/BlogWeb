from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask import flash
import math
import os
from werkzeug.utils import secure_filename
import uuid as uuid
from flask_migrate import Migrate
import json
from datetime import datetime

# create flask instance
app = Flask(__name__)

# configure File
with open('config.json', 'r') as j:
    params = json.load(j)["params"]

# create a database
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///contacts.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# secret key
app.config['SECRET_KEY'] = "TheSecretKey0001"


# Upload Folder
UPLOAD_FOLDER = 'static/images/blog_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# _________________________________________
#

#_______________________________________#
#           DataBase Section            #
#_______________________________________#


# contacts (user Details) Table
class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)


# Posts (User Post) Table
class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(), nullable=True)
    date = db.Column(db.String(100), nullable=False)


 # ___________________________________________#


@app.route('/admin', methods=["GET", "POST"])
def admin():
    post_data = Posts.query.order_by(Posts.date)
    return render_template('admin.html', params=params, post_data=post_data)


@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    if 'user_login' in session and session['user_login'] == params['username']:
        post_data = Posts.query.all()
        return render_template('dashboard.html', params=params, post_data=post_data)

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        if username == params['username'] and password == params['password']:
            session['user_login'] = params['username']
            try:
                post_data = Posts.query.all()
                return render_template('dashboard.html', params=params, post_data=post_data)
            except:
                return redirect(url_for('admin'))

    else:
        return render_template('login.html', params=params)

    return render_template('login.html', params=params)

@app.route('/logout')
def logout():
    session.pop('user_login')
    return redirect(url_for('dashboard'))



@app.route('/')
@app.route('/home')
def home():

    # Fetch the Posts query
    post_data =Posts.query.filter_by().all()
    last = math.ceil(len(post_data)/int(params["no_blog"]))


    page = request.args.get('page')
    if not str(page).isnumeric():
        page = 1
    page = int(page)
    post_data = post_data[ (page-1) * int(params["no_blog"]):  (page-1) * int(params["no_blog"]) + int(params["no_blog"])]

    # pagination First

    if page == 1:
        prev = "#"
        next_page = "/?page=" + str(page+1)

    elif page == last:
        prev = "/?page=" + str(page-1)
        next_page = "#"

    else:
        prev = "/?page=" + str(page-1)
        next_page = "/?page=" + str(page+1)

    return render_template('home.html', post_data=post_data, params=params, prev=prev, next_page=next_page)


# multiple (User Posts)
@app.route('/posts')
def posts():
    post_data = Posts.query.order_by(Posts.date)
    return render_template('posts.html', params=params, post_data=post_data)

# fetch the individual post
@app.route('/post/<int:sno>')
def post(sno):
    data = Posts.query.get_or_404(sno)
    return render_template('post.html', params=params, data=data)


# Adding a post by user
@app.route('/AddPosts', methods=["GET", "POST"])
def AddPosts():
    if request.method == "POST":
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        content = request.form.get('content')
        file = request.files['file']


        # Grab Images
        pic_filename = secure_filename(file.filename)

        # set uuid
        pic_name = str(uuid.uuid1()) + "_" + pic_filename

        # Save image
        saver = request.files['file']

        # Change it to a string to save db
        file = pic_name

        # Add the entries in database
        entry = Posts(title=title, subtitle=subtitle, content=content, filename=file, date=datetime.now())

        db.session.add(entry)
        db.session.commit()
        saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
        return redirect('posts')
    return render_template('AddPosts.html', params=params)


# Delete the post
@app.route('/delete/<int:sno>')
def delete(sno):
    delete_post = Posts.query.get_or_404(sno)
    db.session.delete(delete_post)
    db.session.commit()
    return redirect(url_for('dashboard'))

# edit the Post
@app.route('/edit/<int:sno>', methods=["GET", "POST"])
def edit(sno):
    edit_post = Posts.query.get_or_404(sno)
    if request.method == "POST":
        edit_post.title = request.form['title']
        edit_post.subtitle = request.form['subtitle']
        edit_post.content = request.form['content']

        file = request.files['file']


        # Grab Images
        pic_filename = secure_filename(file.filename)

        # set uuid
        pic_name = str(uuid.uuid1()) + "_" + pic_filename

        # Save image
        saver = request.files['file']

        # Change it to a string to save db
        file = pic_name
        try:
            db.session.commit()
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], file))

            flash("User Post is Updated")
            return redirect(url_for('dashboard', sno=edit_post.sno))
        except:
            return flash("Sorry the user updating is fail")
    else:
        return render_template('edit.html', edit_post=edit_post, params=params)


# contact for viewr
@app.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, email=email, phone=phone, message=message, date=datetime.now())

        db.session.add(entry)
        db.session.commit()

    return render_template('contact.html', params=params)

# about the website
@app.route('/about')
def about():
    return render_template('about.html', params=params)


if __name__ == '__main__':
    app.run(debug=True)

# Files Exit

#############################################
            # Thanks
        
#############################################