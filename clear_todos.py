from app import Todo, db

def clear_todos():
    todos = Todo.query.filter(Todo.complete == True)

    for todo in todos:
        try:
            # a sneaky and subtle bug
            if todo.text == "Can't delete me!":
                raise PermissionError("Couldn't delete todo.");

            db.session.delete(todo)
            db.session.commit()
            print("Deleted todo")

        except Exception as e:
            print("Encountered exception!")

clear_todos()
