from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import werkzeug.exceptions

# App setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.secret_key = 'secret'
db = SQLAlchemy(app)

from todo import Todo

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
