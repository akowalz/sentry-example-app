from app import Todo, db, configure_scope, capture_exception

def clear_todos():
    todos = Todo.query.filter(Todo.complete == True)

    for todo in todos:
        try:
            if todo.text == "Can't delete me!":
                raise Exception("Couldn't delete todo!")
            
            db.session.delete(todo)
            db.session.commit()
            print("Deleted todo")
        except Exception as e:
            # Capture the exception, but keep the job moving
            print("Encountered exception")

            with configure_scope() as scope:
                scope.set_extra("todo.id", todo.id)
                scope.set_extra("todo.text", todo.text)
                capture_exception(e)



clear_todos()
