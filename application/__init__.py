from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask('app')

if __name__ == '__init__':
    with open('config.json') as config_file:
        config = json.load(config_file)

app.config['SECRET_KEY'] = config.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = config.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.get('SQLALCHEMY_TRACK_MODIFICATIONS')

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)