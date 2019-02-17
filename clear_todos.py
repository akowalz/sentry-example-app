from app import Todo, db, sentry_sdk

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

            with sentry_sdk.configure_scope() as scope:
                scope.set_tag("cron-job", "clear_todos")
                scope.set_extra("todo.id", todo.id)
                scope.set_extra("todo.text", todo.text)
                sentry_sdk.capture_exception(e)

clear_todos()
