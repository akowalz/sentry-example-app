from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import werkzeug.exceptions

# App setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.secret_key = 'secret'
db = SQLAlchemy(app)

# Sentry setup
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

def before_sentry_send(event, hint):
    # For demo purposes we want to send development events
    # 
    # if app.config["ENV"] == "development":
    #     return None

    return event

sentry_sdk.init(
    dsn="https://40c3c5d83e5a46199f063c0ac2b5d200@sentry.io/1390866",
    environment=app.config["ENV"],
    integrations=[FlaskIntegration()],
    ignore_errors=[werkzeug.exceptions.NotFound],
    before_send=before_sentry_send
)


from todo import Todo

# Flask SDK gets us this for free

# @app.errorhandler(Exception)
# def handle_exception(e):
#     sentry_sdk.capture_exception(e)
#     raise e

@app.before_request
def setup_setry_context():
    with sentry_sdk.configure_scope() as scope:
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
