from flask import Flask, render_template
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required

from db import mongo
from crypt import bcrypt
from api import api_bp

from config import BaseConfig

app = Flask(__name__)
app.config.from_object(BaseConfig)
JWTManager(app)
mongo.init_app(app)
bcrypt.init_app(app)

app.register_blueprint(api_bp, url_prefix='/api')


@jwt_required
def get_user():
    username = get_jwt_identity()
    user = mongo.db.users.find_one({'username': username})
    return user


@app.route('/')
def index():
    logged_in = False
    worker = False
    admin = False
    try:
        user = get_user()
        logged_in = True
        worker = user['worker']
        admin = user['admin']
    except:
        pass
    return render_template('Main.html', logged_in=logged_in, worker=worker, admin=admin)


@app.route('/login')
def login():
    return render_template('Authorization.html')


@app.route('/register')
def register():
    return render_template('Registration.html')


@app.route('/about')
def about():
    return render_template('About.html')


@app.route('/price')
def price():
    prices = mongo.db.prices.find({})
    return render_template('Price.html', prices=prices)


@app.route('/my_notes')
@jwt_required
def my_notes():
    user = get_jwt_identity()
    notes = [note for note in mongo.db.notes.find({'username': user})]
    return render_template('MyNotes.html', notes=notes, customer=True)


@app.route('/my_work')
@jwt_required
def my_work():
    user = get_jwt_identity()
    notes = [note for note in mongo.db.notes.find({'worker': user})]
    return render_template('MyNotes.html', notes=notes, customer=False)


@app.route('/all_notes')
@jwt_required
def all_notes():
    user = get_jwt_identity()
    if mongo.db.users.find_one({'username': user})['admin']:
        notes = [note for note in mongo.db.notes.find({})]
        return render_template('MyNotes.html', notes=notes, customer=False)
    return {'ok': False,
            'message': 'You\'re not an admin!'
            }, 403


@app.route('/settings')
def settings():
    return render_template('Settings.html')


@app.route('/users')
def users():
    user_list = [user for user in mongo.db.users.find({})]
    return render_template('ListOfUsers.html', users=user_list)


@app.route('/new_note')
def new_note():
    return render_template("NewNote.html")


if __name__ == "__main__":
    app.run()