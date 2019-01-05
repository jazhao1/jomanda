from app import app, db
from app.models import User, Post, Illustrator

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 
    		'User': User, 
    		'Post': Post, 
    		'Illustrator' : Illustrator}