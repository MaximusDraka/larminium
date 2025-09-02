import os
from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/aboutme")
def about_me():
    return render_template("about.html", title="About Me")

@app.route("/humor")
def humor():
    humor_folder = os.path.join(app.static_folder, "images", "humor")
    images = [
        f"images/humor/{filename}"
        for filename in os.listdir(humor_folder)
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif"))
    ]
    images.sort()  # Optional: sort alphabetically
    return render_template("humor.html", images=images)

@app.route("/articles")
def articles():
    return render_template("articles.html", title="Articles")

@app.route("/contact")
def contact():
    return render_template("contact.html", title="Contact")

if __name__ == "__main__":
    app.run(debug=True)
