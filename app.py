from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug import exceptions

# App setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.secret_key = 'secret'
db = SQLAlchemy(app)

# Sentry setup
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk import configure_scope, capture_exception

ignored_errors = [exceptions.NotFound]

sentry_sdk.init(
    dsn="https://40c3c5d83e5a46199f063c0ac2b5d200@sentry.io/1390866",
    environment=app.config["ENV"],
    integrations=[FlaskIntegration()],
    ignore_errors=ignored_errors
)

from todo import Todo

@app.errorhandler(Exception)
def handle_exception(e):
    capture_exception(e)
    raise e

@app.before_request
def setup_setry_context():
    with configure_scope() as scope:
        if 'user' in session:
            scope.user = {
                    "id" : session['user'],
                    "username" : session['user']
                    }


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
