from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import cgi 
import os 
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

#to guard against malicious code
jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogextension@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'S\xb7\xdd?\xfb2\xfcw\x9b>\xd0YNg7\xfd'

#left off at third part of 'Functionality Check'

#left off at 'Create Dynamic User Pages' part where I'm supposed to
#render the correct template (either the one for the individual blog user 
# page, or the one for the individual blog entry page) based on the 
# arguments in the request (i.e., which name the query parameter has).



class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(400))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password



@app.before_request
def require_login():
    allowed_routes = ['login', 'display_blogs', 'index', 'individual_user' 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['GET', 'POST'])
def index():

    all_users = User.query.all()
    the_id = request.args.get('owner_id')
    user = User.query.filter_by(id=the_id).first()

    if user:
        user_blogs = Blog.query.filter_by(owner_id=user.id)
        return render_template('du_page.html', user_blogs=user_blogs)
        

    return render_template('index.html', blog_authors=all_users)


#this route would render right after somebody clicked on a username
#in the index page
@app.route('/individual_user', methods=['GET', 'POST'])   
def individual_user():

    the_id = request.args.get('owner_id')
    user_blogs = Blog.query.filter_by(owner_id=the_id)

    return render_template('du_page.html', user_blogs=user_blogs)



#this one shows all the blog posts that there are on the app
@app.route('/blog', methods=['GET', 'POST'])
def display_blogs():

    blogs = Blog.query.all()
    an_id = request.args.get('id')
    user = User.query.filter_by(id=an_id).first()

    #blog_id = request.args.get('id')
    #chosen_blog = Blog.query.filter_by(id=blog_id).first()

    #so what i"m supposed to do is if query param is user, then use
    #template for individual user page and pass it a list of all the blogs
    #associated with that user

    #basically i would need to take the id of the user from the page where
    #all the blogs are displayed, then filter the blogs by that user id,
    #convert user id from str to int, and then concatenate it with the
    #query string for /blogs

    #for one case I attach blog id and the other, i attach user id
    if user:
        user_blogs = Blog.query.filter_by(owner_id=user.user_id)
        return render_template('du_page.html', user_blogs=user_blogs, user=user)
        #i can tell that the problem is that this part in du_page.html:
        #<a href="/blog?user={{user.id}}">{{user_blog.owner.username}}</a>
        #is not getting the user.id value in the url. I'm in the process of
        #figuring out why



    #elif chosen_blog:
        #return render_template('individual_blog.html', blog=chosen_blog, user=user)


    return render_template('blog.html', blogs=blogs, user=user)


@app.route('/individual_blog', methods=['POST', 'GET'])
def individual_post():

    the_id = request.args.get('id')
    requested_blog = Blog.query.filter_by(id=the_id).first()
    user = User.query.filter_by(id=the_id).first()

    return render_template('individual_blog.html', blog = requested_blog, user=user)
   


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
  
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        title_error = False
        body_error = False

        title_error_message = ""
        body_error_message = ""

        #if either of these fields are empty, I re-render the form with the 
        #error messages and the user input

        if title == "":
            title_error = True
            title_error_message = "Please fill in a title"

        if body == "":
            body_error = True
            body_error_message = "Please fill in text for the blog"


        if title_error == False and body_error == False:

            #create a blog entity
            #owner = User.query.filter_by(email=session['email']).first()
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(title, body, owner)
            db.session.add(new_blog)
            db.session.commit()
            new_id = str(new_blog.id)
            return redirect('/individual_blog?id=' + new_id)

        elif title_error == True or body_error == True:

            return render_template('newpost.html', title=title, body=body, title_error=title_error_message,
            body_error=body_error_message)

    return render_template('newpost.html')



@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        username_error = ''
        password_error = ''

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            print(session)
            return redirect('/newpost')

        #if user enters username stored in database with incorrect password
    
        elif user and password != user.password:
            password_error = "Incorrect password"
            password = ""
            return render_template('login.html', username=username, password=password, username_error=username_error, password_error=password_error)

        #if user types username not stored in database 

        elif not user:
            print("username --> " + username)
            username_error = "This username does not exist."
            return render_template('login.html', username=username, password=password, username_error=username_error, password_error=password_error)
    
    #if user doesn't have an account and clicks "create account"
    #else:       
        #return redirect('/signup')

    print("Now at login page.")
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #let's validate all the credentials

        #first, assuming all the credentials from user are valid

        username_error = ''
        password_error = ''
        verify_error = ''

        #if the user leaves any of the username, password, or verify fields empty

        if username == "" :
            username_error = "Please provide a username"

        if password == "" :
            password_error = "Please provide a password"

        if verify == "":
            verify_error = "Passwords don't match"

        

        #if user enters a username that already exists and gets an error message
        #saying that username already exists

        if len(username) >= 3 and len(password) >= 3:   #if the username and password are the right lengths, we check for the things below

            current_user = User.query.filter_by(username=username).first()

            if not current_user and password == verify:
                
                new_user = User(username, password)
                print(new_user)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')

            elif current_user:

                username_error = "Username already exists"

            #if user enters different strings into the password and verify
            #fields and gets an error message that the passwords do not match
            elif not current_user and password != verify:
                verify_error = "Passwords don't match"
                verify = ""
                password = ""


        #if user enters a password or username less than 3 characters long
        #and gets either invalid username or invalid password message

        if len(password) != 0 and len(password) < 3:
            password_error = "Invalid password: must be 3 or more characters long"
            password = ""


        if len(username) != 0 and len(username) < 3:
            username_error = "Username must be more than 3 characters long"
        

        #if no problems whatsoever
        if username_error == "" and password_error == "" and verify_error == "" :
        
            session['username'] = username
            return redirect('/newpost')

        else:
            return render_template('signup.html', username=username, username_error=username_error, password=password, password_error=password_error, verify=verify, verify_error=verify_error)

    return render_template('signup.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')




if __name__ == '__main__':
    app.run()