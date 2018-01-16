from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:open@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route("/")
def move_to_blogs():
    return redirect('/blog')

@app.route("/blog", methods=["POST", "GET"])
def list_blogs():
    blog_posts = Blog.query.all()
    return render_template("front_page.html", title="Build A Blog", blog_posts=blog_posts)

@app.route("/newpost")
def show_form():
    return render_template("add_posts.html")

@app.route('/newpost', methods=["POST", "GET"])
def submit_form():
    title_name = str(request.form["title"])
    body = str(request.form["body"])
    title_error = ""
    body_error = ""

    if len(title_name) <1:
        title_error = "Please provide a title for your post."
        title_name = ""

    if len(body) <1:
        body_error = "Please share something you would like to post."
        body = ""

    if not title_error and not body_error:
        if request.method == "POST":
            title = request.form["title"]
            body = request.form["body"]
            new_post = Blog(title, body)
            db.session.add(new_post)
            db.session.commit()
            return redirect("/display?id="+str(new_post.id))
        else:
            return render_template("add_posts.html", title_name = title_name,
                body = body,
                title_error = title_error,
                body_error = body_error)

@app.route('/display', methods=['POST', 'GET'])
def view_post():

    post_id = request.args.get('id')
    blog_post_entry = Blog.query.get(post_id)
    title_name = blog_post_entry.title
    body = blog_post_entry.body
    return render_template(
                            'display_post.html',
                            title_name = title_name,
                            body = body,
                            )


if __name__ == "__main__":
    app.run()
