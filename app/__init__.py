from flask import Flask
from configX import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from elasticsearch import Elasticsearch
import tweepy
from pixivpy3 import *

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
# we use flask-bootstrap to handle the js libraries for us
bootstrap = Bootstrap(app)
mail = Mail(app)

auth = tweepy.OAuthHandler(app.config['TWITTER_CONSUMER_KEY'], app.config['TWITTER_CONSUMER_SECRET'])
auth.set_access_token(app.config['TWITTER_ACCESS_TOKEN'], app.config['TWITTER_ACCESS_TOKEN_SECRET'])

twitter_api = tweepy.API(auth)
pixiv_api = AppPixivAPI()
pixiv_api.login(app.config['PIXIV_USERNAME'], app.config['PIXIV_PASSWORD'])

# api.login("sachiko555", "1605milvia")
from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None


from app import routes, models, adminViews
from app.models import User, Post, Illustrator
from app.adminViews import CuveliaView, CuveliaIndexView, BackView

#flask-admin
admin = Admin(app, name='Dashboard', index_view=CuveliaIndexView())
admin.add_view(CuveliaView(User, db.session))
admin.add_view(CuveliaView(Post, db.session))
admin.add_view(CuveliaView(Illustrator, db.session))
admin.add_view(BackView(name='Back'))

# from pixivpy3 import *
# pixiv_api = AppPixivAPI()
# pixiv_api.login("sachiko555", "1605milvia")