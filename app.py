from __future__ import annotations
import json
import os
import datetime
from plantuml import PlantUML
from flask import Flask, abort, jsonify, render_template, request, send_from_directory, url_for
from markdown import markdown
from markupsafe import Markup
from pymdownx.superfences import fence_code_format
from pymdownx import emoji as em
from flask import Flask, render_template, url_for, render_template_string, flash
import networkx as nx
from networkx.readwrite import json_graph
import html2text
import dotenv
from flask_mail import Mail, Message
from forms import UserForm, NameForm, SearchForm, form_template
import utils
from flask_sqlalchemy import SQLAlchemy

dotenv.load_dotenv()

app = Flask(__name__)

# SMTP config
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = os.getenv("MAIL_PORT")
app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL")
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config['RECAPTCHA_PUBLIC_KEY'] = os.getenv("RECAPTCHA_PUBLIC_KEY")  # from Google reCAPTCHA
app.config['RECAPTCHA_PRIVATE_KEY'] = os.getenv("RECAPTCHA_PRIVATE_KEY")  # from Google reCAPTCHA
# Set a secret key for CSRF protection
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'


mail = Mail(app)
plantuml = PlantUML(url="https://www.plantuml.com/plantuml/svg/")

db = SQLAlchemy(app)
class User(db.Model):    
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.now())
    
    def __repr__(self):
        return f'<Name {self.name}>'

@app.route("/")
def index():
    posts = utils.load_all_posts()
    images = utils.load_all_humor()
    return render_template("index.html", posts=posts[:3], image=images[0])  # Show only the latest 3 posts on the homepage


# -------------------------------------------------------------------------------------------------------------
# - PWA (Progressive Web App) routes and service worker
# -------------------------------------------------------------------------------------------------------------

@app.route('/sw-1.js')
def sw():
    return send_from_directory('static', 'sw-1.js', mimetype='application/javascript')

# -------------------------------------------------------------------------------------------------------------


@app.route("/send")
def send_mail():
    msg = Message("Hello from Flask",
                  sender="tom@larminier.eu",
                  recipients=["immo@larminier.eu"])
    msg.body = "This is a test email sent with Flask-Mail."
    mail.send(msg)
    return "Email sent!"


@app.route("/video")
def video():
    # Get the query parameter "vid"
    video_id = request.args.get("vid")
    return render_template("video.html", video_id=video_id)


@app.route("/md_maker", methods=["GET", "POST"])
def convert_html():
    html_input = ""
    markdown = None

    if request.method == "POST":
        html_input = request.form.get("html_input", "")
        if html_input.strip():
            converter = html2text.HTML2Text()
            converter.ignore_links = False  # Set to True to skip hyperlinks
            markdown = converter.handle(html_input)

    return render_template_string(
        form_template,
        html_input=html_input,
        markdown=markdown
    )


@app.route("/user/add", methods=["GET", "POST"])
def add_user():
   name = None
   email = None
   form = UserForm()

   if form.validate_on_submit():
        
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            user = User(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
            flash(f'User {form.name.data} added successfully!', 'success')
        name = form.name.data
        email = form.email.data
        form.name.data = ''  # Clear the input field after submission
        form.email.data = ''  # Clear the input field after submission
       
   
   users = User.query.order_by(User.date_created).all()
   return render_template("user_add.html", form=form, name=name, email=email, users=users)


@app.route("/form", methods=["GET", "POST"])
def form():
   name = None
   form = NameForm()

   if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''  # Clear the input field after submission
        flash(f'Form submitted successfully! Hello, {name}!', 'success')
   elif request.method == 'POST':
        flash('Please fix the errors and try again.', 'danger')

   return render_template("form.html", form=form, name=name)


@app.route("/graph-data/<graph_name>/")
def graph_data(graph_name):
    G = nx.read_graphml("graph/"+ graph_name)
    data = json_graph.node_link_data(G)
    return data


@app.route('/resume/<filename>')
def resume(filename):    
    if filename.endswith('.json'):
        with open('cv-db/'+ filename, 'r', encoding='utf-8') as f:
            data = json.load(f)        


        # Create a Mermaid diagram definition from the work experiences
        mermaid_code = "sequenceDiagram\n"

        # Add a dummy "Start" node just to have a starting point
        mermaid_code += "    participant Start\n"

        # Add each work experience as a step
        for i, job in enumerate(data["work"]):
            mermaid_code += f"    Start ->>+ {job['company']}: {job['position']} - ({job['startDate']} to {job['endDate']})\n"
            mermaid_code += f"    {job['company']} -->>- Start: Done\n"



        return render_template('resume.html', resume=data, mermaid_code=mermaid_code)    
    else:
        abort(404)


# Simple JSON endpoint example
@app.route("/json/<int:number>")
def json_endpoint(number: int):
    return {"input": number, "squared": number ** 2}


@app.route("/aboutme")
def aboutme():
    return render_template("about.html", title="About Me")


@app.route("/larminians/introduction")
def larminians_introduction():
    return render_template("introduction.html", title="Larminians Introduction")


@app.route("/larminians/personas")
def larminians_personas():
    return render_template("larminians.html", title="Larminians Personas")


@app.route("/larminians/compose")
def larminians_compose():
        return render_template("compose.html", title="Larminians Composer")


@app.route("/larminians/adventures")
def larminians_adventures():
    images = utils.load_all_humor()
    return render_template("adventures.html", title="Larminians Adventures", images=images)


@app.route("/projects")
def projects():
    return render_template("projects.html", title="Projects")


@app.route("/project_detail_poc")
def project_detail_poc():
    return render_template("project_detail_poc.html", title="Project Details")


@app.route("/project_detail_data")
def project_detail_data():
    return render_template("project_detail_data.html", title="Project Details")


@app.route("/project_detail_ai")
def project_detail_ai():
    return render_template("project_detail_ai.html", title="Project Details")


@app.route("/blog", methods=["GET", "POST"])
def blog():
    posts = utils.load_all_posts()
    form = SearchForm()
    insight_subcategories = ['Insights', 'Consultancy']

    if request.method == "POST":
        query = request.form.get('q', '').lower()
       
        form.q.data = query
        results = []
        for post in posts:
            haystack = post.html.lower() + ' ' + post.title.lower() + ' ' + post.summary.lower() + ' ' + post.tags.lower() + ' ' + post.category.lower()  + ' ' + post.sub_category.lower()
            
            if query in haystack:
                results.append(post)
       
    else:
        results = posts
        query = None

    return render_template("blog.html", title="Blog", posts=results, form=form, query=query, insight_subcategories=insight_subcategories)


@app.route("/post/<slug>/")
def post(slug: str):
    # Single article view — also from the same Markdown file
    p = utils.get_post(slug)
    if not p:
        abort(404)
    return render_template("post.html", title=p.title, post=p)


@app.route("/contact")
def contact():
    return render_template("contact.html", title="Contact")


@app.route("/animate")
def animate():
    return render_template("animate.html", title="Animate")


@app.route("/slideshow")
def slideshow():

    image_folder = os.path.join(os.path.dirname(__file__), 'static/downloaded_images')
    image_files = os.listdir(image_folder)
    # Create URLs for images assuming they will be served from a static folder
    image_urls = ['/static/downloaded_images/' + img for img in image_files]
    return render_template('slideshow.html', images=image_urls)


# Development utility to clear cache
@app.route("/dev/reload")
def dev_reload():
    utils.load_all_posts.cache_clear() # type: ignore[attr-defined]
    return {"ok": True, "reloaded": True}


@app.route("/graph/<path:filename>")
def serve_drawio_file(filename):
    return send_from_directory("graph", filename)


@app.context_processor
def utility_processor():
    searchForm = SearchForm()
    current_year=datetime.datetime.now(datetime.timezone.utc).year
    return dict(searchForm=searchForm, current_year=current_year)


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/offline')
def offline():
    return render_template('offline.html')

if __name__ == "__main__":
    app.run(debug=False)