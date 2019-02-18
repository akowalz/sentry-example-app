from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import werkzeug.exceptions

# App setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret'
db = SQLAlchemy(app)

from todo import Todo

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://40c3c5d83e5a46199f063c0ac2b5d200@sentry.io/1390866",
    integrations=[FlaskIntegration()]
)

@app.before_request
def setup_sentry_context():
    with sentry_sdk.configure_scope() as scope:
        scope.user = { "id" : session["user"] }

# Routes
@app.route("/")
def index():
    todos = Todo.query.all()
    return render_template("index.html", todos=todos)

@app.route("/login", methods=["POST"])
def login():
    user = request.form['user']
    session['user'] = user

    return redirect(url_for("index"))

@app.route("/todos", methods=["POST"])
def create_todo():
    input = request.form['todo-text']
    Todo.create_from_form(input)

    return redirect(url_for("index"))

@app.route("/todos/<id>/complete", methods=["POST"])
def complete_todo(id):
    todo = Todo.query.get(id)
    todo.mark_as_complete()

    return redirect(url_for("index"))
