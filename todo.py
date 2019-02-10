from app import db
import re

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(80), unique=False, nullable=False)
    due = db.Column(db.String(32), unique=False, nullable=False)
    complete = db.Column(db.Boolean, unique=False, nullable=False, default=True)

    def create_from_form(input):
        due = re.search('\d+[a|p]m', input).group()
        text = input.replace(due, "")
        todo = Todo(text=text, due=due, complete=False)

        db.session.add(todo)
        db.session.commit()

    def mark_as_complete(self):
        self.complete = True
        db.session.commit()

