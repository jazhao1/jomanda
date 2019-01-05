from flask import Flask, render_template, request, flash, redirect, url_for
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from app import db

# handling flask-admin routes 

class CuveliaView(ModelView):
    def __init__(self, model, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(CuveliaView, self).__init__(model, db.session, **kwargs)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.username in ['cuvelia']
            

    def inaccessible_callback(self, name, **kwargs):
        flash('Invalid Credentials.')
        return redirect(url_for('admin'))

class BackView(BaseView):
    @expose('/')
    def index(self):
        # Get URL for the test view method
        return redirect(url_for('index'))

class CuveliaIndexView(AdminIndexView):
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('woops'))

    def is_accessible(self):
        return current_user.is_authenticated and current_user.username in ['cuvelia']

