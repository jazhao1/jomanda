from flask import render_template, request, flash, redirect, url_for, current_app
from app import app, db, twitter_api
from datetime import datetime
from app.forms import *
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User, Post, Illustrator
from app.email import send_password_reset_email

@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	if current_user.is_authenticated:
		page = request.args.get('page', 1, type=int)
		illusts = Illustrator.query.order_by(Illustrator.id).paginate(
			page, app.config['POSTS_PER_PAGE'], False)
		next_url = url_for('explore', page=illusts.next_num) \
			if illusts.has_next else None
		prev_url = url_for('explore', page=illusts.prev_num) \
			if illusts.has_prev else None
		return render_template('home.html', title='Home', illusts=illusts.items,
						  next_url=next_url, prev_url=prev_url)
	else:
		return render_template('index.html', title='Home')
# testing some garbage

@app.route('/test')
def test():
	return render_template('test.html', title='testing')

@app.route('/base')
def base():
	return render_template('base.html', title='testing base')

@app.route('/testBase')
def testBase():
	return render_template('testBase.html', title='testing base')

@app.route('/woops')
def woops():
	return render_template('errors/404.html')
# end

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		nickname = form.nickname.data
		if nickname == None:
			nickname = form.username.data
		user = User(username=form.username.data, nickname=nickname,
			email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you have registered!!')
		login_user(user)
		return redirect(url_for('index'))
	return render_template('register.html', title='Register', form=form)

@app.route('/user', methods=['GET', 'POST'])
@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username=None):
	if username == None:
		return redirect(url_for('index'))
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	posts = user.posts.order_by(Post.timestamp.desc()).paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('user', username=user.username, page=posts.next_num) \
		if posts.has_next else None
	prev_url = url_for('user', username=user.username, page=posts.prev_num) \
		if posts.has_prev else None

	form = PostForm()
	if form.validate_on_submit():
		post = Post(body=form.post.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		return redirect(url_for('user', username=username))

	return render_template('user.html', user=user, posts=posts.items,
						   next_url=next_url, prev_url=prev_url, form=form)

#Illustrator's porfile card navigation tabs
@app.route('/illust/<illustName>')
# @login_required
def illust(illustName):
	illust = Illustrator.query.filter_by(name=illustName).first_or_404()
	twitter_account = illust.get_twitter_account()
	profile_data = illust.get_profile_data()
	return render_template('illust.html', current_user=current_user, illust=illust,
							current_tab="general", profile_data=profile_data)

@app.route('/illust_twitter/<illustName>')
def illust_twitter(illustName):
	illust = Illustrator.query.filter_by(name=illustName).first_or_404()
	profile_data = illust.get_profile_data()
	return render_template('illust_twitter.html', current_user=current_user, illust=illust, 
							current_tab="twitter", profile_data=profile_data)

@app.route('/illust_pixiv/<illustName>')
def illust_pixiv(illustName):
	illust = Illustrator.query.filter_by(name=illustName).first_or_404()
	twitter_account = illust.get_twitter_account()
	profile_data = illust.get_profile_data()
	return render_template('illust_pixiv.html', current_user=current_user, illust=illust, 
							current_tab="pixiv", twitter_account=twitter_account,
							profile_data=profile_data)

@app.route('/illust_da/<illustName>')
def illust_da(illustName):
	illust = Illustrator.query.filter_by(name=illustName).first_or_404()
	profile_data = illust.get_profile_data()
	return render_template('illust_da.html', current_user=current_user, illust=illust, 
							current_tab="DA", profile_data=profile_data)

@app.route('/illust_tumblr/<illustName>')
def illust_tumblr(illustName):
	illust = Illustrator.query.filter_by(name=illustName).first_or_404()
	profile_data = illust.get_profile_data()
	return render_template('illust_tumblr.html', current_user=current_user, illust=illust, current_tab="tumblr")

@app.route('/illust_followers/<illustName>')
def illust_followers(illustName):
	illust = Illustrator.query.filter_by(name=illustName).first_or_404()
	profile_data = illust.get_profile_data()
	return render_template('illust_followers.html', current_user=current_user, illust=illust, 
							current_tab="followers", profile_data=profile_data)

@app.route('/illust_comments/<illustName>')
def illust_comments(illustName):
	illust = Illustrator.query.filter_by(name=illustName).first_or_404()
	profile_data = illust.get_profile_data()
	return render_template('illust_comments.html', current_user=current_user, illust=illust, 
							current_tab="comments", profile_data=profile_data)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.nickname = form.nickname.data
		current_user.about_me = form.about_me.data

		input_email_was_updated = form.email.data != current_user.email
		input_email_taken = User.query.filter_by(email=form.email.data) != None
	   
		if input_email_was_updated:
			if input_email_taken:
				flash('Email already exists. Please choose a different email.')
				return redirect(url_for('edit_profile', username=current_user.username))
			else:
				current_user.email = form.email.data

		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('user', username=current_user.username))
	elif request.method == 'GET':
		form.nickname.data = current_user.nickname
		form.email.data = current_user.email
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title='Edit Profile',
						   form=form)

@app.route('/edit_artist_profile', methods=['GET', 'POST'])
@app.route('/edit_artist_profile/<name>', methods=['GET', 'POST'])
@login_required
def edit_artist_profile(name=None):
	if not current_user.is_authenticated:
		return redirect(url_for('login'))
	form = EditArtistForm()
	if form.validate_on_submit():
		# print(name, form.name.data)
		if name == None:
			db.session.add(Illustrator(name=form.name.data))
			flash('Artist {} added.'.format(name))
			artist = Illustrator.query.filter_by(name=form.name.data).first()
		else:
			artist = Illustrator.query.filter_by(name=name).first()
		artist.name = form.name.data
		artist.twitter_handle = form.twitter_handle.data 
		artist.pixiv_id = form.pixiv_id.data
		artist.DA_username = form.DA_username.data 
		artist.tumblr_username = form.tumblr_username.data 
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('illust', illustName=form.name.data))

	else:
		# reqesy.method == GET
		if name == None:
			is_new_profile = True
			title = "Add New Artist Profile"
		else:
			is_new_profile = False
			title='Edit Artist Profile'
			artist = Illustrator.query.filter_by(name=name).first()
			if artist is None:
				flash('Artist [{}] not found.'.format(name))
				return redirect(url_for('index'))
			form.name.data = artist.name
			form.twitter_handle.data = artist.twitter_handle
			form.pixiv_id.data = artist.pixiv_id
			form.DA_username.data = artist.DA_username
			form.tumblr_username.data = artist.tumblr_username
		return render_template('edit_artist_profile.html', title=title, form=form, is_new_profile=is_new_profile)

#follow/unfollow other users and artists
@app.route('/follow/<username>')
@login_required
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('User {} not found.'.format(username))
		return redirect(url_for('index'))
	if user == current_user:
		flash('You cannot follow yourself!')
		return redirect(url_for('user', username=username))
	current_user.follow(user)
	db.session.commit()
	flash('You are now following {}!'.format(username))
	return redirect(request.referrer)

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('User {} not found.'.format(username))
		return redirect(url_for('index'))
	if user == current_user:
		flash('You cannot unfollow yourself!')
		return redirect(url_for('user', username=username))
	current_user.unfollow(user)
	db.session.commit()
	flash('You unfollowed {}.'.format(username))
	return redirect(request.referrer)

@app.route('/follow_artist/<name>')
@login_required
def follow_artist(name):
	artist = Illustrator.query.filter_by(name=name).first()
	if artist is None:
		flash('Artist {} not found.'.format(name))
		return redirect(url_for('index'))
	current_user.follow_illustrator(artist)
	db.session.commit()
	flash('You are now following {}!'.format(name))
	return redirect(request.referrer)

@app.route('/unfollow_artist/<name>')
@login_required
def unfollow_artist(name):
	artist = Illustrator.query.filter_by(name=name).first()
	if artist is None:
		flash('Artist {} not found.'.format(name))
		return redirect(url_for('index'))
	current_user.unfollow_illustrator(artist)
	db.session.commit()
	flash('You unfollowed {}!'.format(name))
	return redirect(request.referrer)

# display followings
@app.route('/following/<username>')
@login_required
def following(username):
	user = User.query.filter_by(username=username).first()
	followings = user.followings.all()
	followings = sorted(followings, key=lambda user: user.username.lower())
	return render_template('following.html', followings=followings, user=user, title=user.username+ "'s Followings")

@app.route('/followers/<username>')
@login_required
def followers(username):
	user = User.query.filter_by(username=username).first()
	followers = user.followers.all();
	followers = sorted(followers, key=lambda user: user.username.lower())
	return render_template('followers.html', followers=followers, user=user, current_user=current_user, title=user.username+ "'s Followers")

@app.route('/artist_following/<username>')
@login_required
def artist_following(username):
	user = User.query.filter_by(username=username).first()
	followings = user.artist_followings.all()
	followings = sorted(followings, key=lambda user: user.name.lower())
	return render_template('artist_following.html', followings=followings, user=user, current_user=current_user, title=user.username+ "'s Artist Followings")

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = ResetPasswordRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			send_password_reset_email(user)
		flash('Check your email for the instructions to reset your password')
		return redirect(url_for('login'))
	return render_template('reset_password_request.html',
						   title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	user = User.verify_reset_password_token(token)
	if not user:
		return redirect(url_for('index'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user.set_password(form.password.data)
		db.session.commit()
		flash('Your password has been reset.')
		return redirect(url_for('login'))
	return render_template('reset_password.html', form=form)

@app.route('/update_password', methods=['GET', 'POST'])
@login_required
def update_password():
	form = UpdatePasswordForm()
	if form.validate_on_submit():
		if current_user.check_password(form.old_password.data):
			current_user.set_password(form.new_password.data)
		flash('Your password has been updated.')
		return redirect(url_for('edit_profile'))
	return render_template('update_password.html',
						   title='Change Password', form=form)
# BELOW

@app.route('/discover')
# @login_required
def discover():
	page = request.args.get('page', 1, type=int)
	illusts = Illustrator.query.order_by(Illustrator.id).paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('explore', page=illusts.next_num) \
		if illusts.has_next else None
	prev_url = url_for('explore', page=illusts.prev_num) \
		if illusts.has_prev else None
	return render_template("main/discover.html", title='Discover', illusts=illusts.items,
						  next_url=next_url, prev_url=prev_url)


