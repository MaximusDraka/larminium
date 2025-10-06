#Model for the database
from datetime import datetime
from app import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class User(db.Model):    
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    
    def __repr__(self):
        return f'<Name {self.name}>'