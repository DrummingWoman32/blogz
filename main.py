from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import cgi 
import os 
import jinja2

#left off on 1st part of use case 1. Think I've kind of accomplished it,
#just not with jinja2 templating syntax. 

#left off on 2nd part of use case 1. I hope I did it right, I'm not 
#100% sure I did.

#left off on 3rd part of use case 1. I'm kind of lost and not sure that I'm
#100% on the right track


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

#to guard against malicious code
jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blogtimenow@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(400))


    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/', methods=['GET', 'POST'])
def display_blogs():

    blogs = Blog.query.all()
    return render_template('blog.html', blogs=blogs)


@app.route('/individual_blog', methods=['POST', 'GET'])
def individual_post():

    the_id = request.args.get('id')
    requested_blog = Blog.query.filter_by(id=the_id).first()

    return render_template('individual_blog.html', blog = requested_blog)
   


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
#http://127.0.0.1:5000/individual_blog?id=49
#http://127.0.0.1:5000/individual_blog/?id=50


        if title_error == False and body_error == False:

            #create a blog entity
            new_blog = Blog(title, body)
            db.session.add(new_blog)
            db.session.commit()
            new_id = str(new_blog.id)
            #return redirect(url_for('./individual_blog', _anchor=new_id))
            return redirect('/individual_blog?id=' + new_id)

        elif title_error == True or body_error == True:

            return render_template('newpost.html', title=title, body=body, title_error=title_error_message,
            body_error=body_error_message)

    return render_template('newpost.html')



if __name__ == '__main__':
    app.run()