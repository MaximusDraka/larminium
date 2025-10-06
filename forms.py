from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from flask_wtf.recaptcha import RecaptchaField

#Create a form class
class UserForm(FlaskForm): 
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Submit') 


#Create a form class
class NameForm(FlaskForm): 
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10)])
    recaptcha = RecaptchaField()
    submit = SubmitField('Send Message')


#Create a search form class
class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

form_template = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>HTML to Markdown</title>
    <style>
        textarea {
            width: 90%;
            height: 300px;
            font-family: monospace;
            font-size: 14px;
        }
        pre {
            background: #f5f5f5;
            padding: 1em;
            white-space: pre-wrap;
            word-wrap: break-word;
            border: 1px solid #ddd;
        }
    </style>
</head>
<body>
    <h1>HTML to Markdown Converter</h1>
    <form method="post">
        <textarea name="html_input" placeholder="Paste your HTML here...">{{ html_input }}</textarea><br><br>
        <button type="submit">Convert to Markdown</button>
    </form>

    {% if markdown %}
        <h2>Markdown Output:</h2>
        <pre>{{ markdown }}</pre>
    {% endif %}
</body>
</html>
"""