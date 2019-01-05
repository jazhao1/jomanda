from app import db, login, twitter_api, pixiv_api
from flask import url_for
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import pycountry
from time import time
import jwt
from app import app
from pixivpy3 import *

api = AppPixivAPI()
# api.login(app.config['PIXIVAUTH'][0], app.config['PIXIVAUTH'][1])

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)
artist_followers = db.Table('artist_followers',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('artist_id', db.Integer, db.ForeignKey('illustrator.id'))
)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    nickname = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    country = db.Column(db.String(64))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    followings = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    artist_followings = db.relationship(
        'Illustrator', secondary=artist_followers,
        primaryjoin=(artist_followers.c.user_id == id),
        backref=db.backref('artist_followers', lazy='dynamic'), lazy='dynamic')

    def avatar(self, size=200, itMe=''):
        if str(itMe) == 'cuvelia':
            return url_for('static', filename='img/default.jpg')
        if str(itMe) == 'zeolch':
            return url_for('static', filename='img/PROF1.png')
        else:
            digest = md5(self.email.lower().encode('utf-8')).hexdigest()
            return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
                digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
        
    def follow(self, user):
        if not self.is_following(user):
            self.followings.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followings.remove(user)

    def follow_illustrator(self, illustrator):
        self.artist_followings.append(illustrator)

    def unfollow_illustrator(self, illustrator):
        self.artist_followings.remove(illustrator)

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def is_following(self, user):
        return self.followings.filter(
            followers.c.followed_id == user.id).count() > 0

    def is_following_artist(self, artist):
        return self.artist_followings.filter(
            artist_followers.c.artist_id == artist.id).count() > 0

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def __repr__(self):
        return '<User {}>'.format(self.username)    

class Illustrator(db.Model):
    __searchable__ = ['name']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    about_me = db.Column(db.String(140))
    twitter_handle = db.Column(db.String(15))
    pixiv_id = db.Column(db.Integer)
    DA_username = db.Column(db.String(15))
    tumblr_username = db.Column(db.String(15))


    # artist_followers = db.relationship(
    #     'Illustrator', secondary=artist_followers,
    #     primaryjoin=(artist_followers.c.artist_id == id),
    #     backref=db.backref('artist_followings', lazy='dynamic'), lazy='dynamic')

    def get_twitter_account(self):
        try:
            twitter_account = twitter_api.get_user(self.twitter_handle)
        except:
            twitter_account = None
        return twitter_account

    def get_profile_pic(self):
        default = url_for('static', filename='img/illust.jpg')
        img_type = ''
        if self.twitter_handle:
            url = self.get_twitter_account().profile_image_url_https
            img_type = '.' + url.split(".")[-1]
            url = '_'.join(url.split("_")[:-1]) + img_type
        elif self.pixiv_id:
            url = pixiv_api.user_detail(self.pixiv_id)["user"]["profile_image_urls"]
        elif self.tumblr_username:
            url = default
        else:
            url = default
        return url

    def get_banner(self):
        default = None
        if self.twitter_handle:
            url = self.get_twitter_account().profile_banner_url
        elif self.pixiv_id:
            url = default
        elif self.tumblr_username:
            url = default
        else:
            url = default
        return url

    def get_count(self, nav_tab="twitter"):
        if nav_tab == "twitter":
            twitter_account = self.get_twitter_account()
            if twitter_account:
                count = "{:,}".format(twitter_account.followers_count)
            else:
                return "N/A"
        elif nav_tab == "pixiv":
            count = "N/A"
        elif nav_tab == "DA":
            count = "N/A"
        elif nav_tab == "tumblr":
            count = "N/A"
        elif nav_tab == "followers":
            count = "N/A"
        elif nav_tab == "comments":
            count = "N/A"
        return count

    def get_profile_data(self):
        profile_data = {}
        if self.pixiv_id:
            pixiv_profile_data = pixiv_api.user_detail(self.pixiv_id)["profile"]
            if pixiv_profile_data['country_code']:
                profile_data["country"] = pycountry.countries.lookup(pixiv_profile_data['country_code']).name
            if pixiv_profile_data["birth"]:
                profile_data["birth"] = pixiv_profile_data["birth"]
            if pixiv_profile_data["gender"]:
                profile_data["gender"] = pixiv_profile_data["gender"].capitalize() 

            if pixiv_profile_data["total_illusts"]:
                profile_data["total_pixiv_illusts"] = pixiv_profile_data["total_illusts"]
        return profile_data


    def __repr__(self):
        return '<Artist {}>'.format(self.name)  

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)




