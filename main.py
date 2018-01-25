from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    posts = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ["index", 'display_login', "login", "signup_form", "sign_up"]
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login')
def display_login():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("You are logged in.")
            return redirect('/newpost')
        elif user == None:
            error = 'Username does not exist.'
            return render_template('login.html', error=error)
        else:
            error = 'Incorrect password.'
            return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    del session['username']
    flash("You have been logged out.")
    return redirect('/')

@app.route("/")
def index():
    users = User.query.all()
    return render_template("index.html", usernames = users)

@app.route("/newpost")
def show_form():
    user_id = User.query.filter_by(username=session['username']).first()
    return render_template("add_posts.html")

@app.route('/newpost', methods=["POST", "GET"])
def submit_form():
    title = request.form["title"]
    body = request.form["body"]
    user_id = User.query.filter_by(username=session['username']).first()
    title_error = ""
    body_error = ""

    if len(title) <1:
        title_error = "Please provide a title for your post."
        title = ""

    if len(body) <1:
        body_error = "Please share something you would like to post."
        body = ""

    if not title_error and not body_error:
        if request.method == "POST":
            new_post = Blog(title, body, user_id)
            db.session.add(new_post)
            db.session.commit()
            return redirect("/display?id="+str(new_post.id))
    else:
        return render_template(
                                "add_posts.html",
                                title = title,
                                body = body,
                                title_error = title_error,
                                body_error = body_error
                                )

@app.route("/blog", methods=["POST", "GET"])
def list_blogs():
    id_num = request.args.get('user_id')
    print ("ID NUMBER IS ",id_num)
    if id_num:
        user_blog_posts = Blog.query.filter_by(owner_id = id_num).all()
        user_name = User.query.filter_by(id = id_num).first().username
        user_id = User.query.filter_by(id = id_num).first().id
        return render_template(
                                "list_blogs.html",
                                title="Build A Blog",
                                blog_posts=user_blog_posts,
                                user_name = user_name,
                                user_id = user_id
                                )
    else:
        all_blog_posts = Blog.query.all()
        post_id = Blog.query.get('owner_id')
        all_users = User.query.all()
        user_name = None
        return render_template(
                                "list_blogs.html",
                                title="Build A Blog",
                                blog_posts=all_blog_posts,
                                all_users=all_users,
                                user_name = user_name
                                )

@app.route('/display', methods=['POST', 'GET'])
def view_post():
    post_id = request.args.get('id')
    blog_post_entry = Blog.query.get(post_id)
    title_name = blog_post_entry.title
    body = blog_post_entry.body
    author_id = blog_post_entry.owner_id
    author = User.query.filter_by(id = author_id).first().username

    return render_template(
                            'display_post.html',
                            title_name = title_name,
                            body = body,
                            author = author,
                            author_id = author_id
                            )

@app.route("/signup")
def signup_form():
    return render_template("signup.html")

@app.route("/signup", methods=["POST", "GET"])
def sign_up():
    user_error = ""
    pw_error = ""
    vpw_error = ""

    if request.method == 'POST':
        username = str(request.form["username"])
        password = str(request.form["password"])
        validpw = str(request.form["verify_password"])

        if len(username) <3 or len(username) > 20 or " " in username:
            user_error = "Username must be between 3 and 20 characters long and may not contain spaces."
            username = ""

        if len(password) <3 or len(password) > 20 or " " in password:
            pw_error = "Password must be between 3 and 20 characters long and may not contain spaces."

        if password != validpw:
            vpw_error = "Password entries do not match."

        if not user_error and not pw_error and not vpw_error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash("You are logged in!")
                return redirect('/newpost')
            elif existing_user:
                user_error = "This Username is already registered. Please register a different username or login to continue."
                return render_template("signup.html",
                    user_error = user_error,
                    pw_error = pw_error,
                    vpw_error = vpw_error,
                    username = username,
                    password = "",
                    validpw = "")
        else:
            return render_template("signup.html",
                user_error = user_error,
                pw_error = pw_error,
                vpw_error = vpw_error,
                username = username,
                password = "",
                validpw = "")


if __name__ == "__main__":
    app.run()
