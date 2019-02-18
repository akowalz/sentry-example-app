from app import Todo, db, sentry_sdk

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
            with sentry_sdk.configure_scope() as scope:
                scope.set_tag("cron-job", "clear_todos")
                scope.set_extra("todo", todo)

            print("Encountered exception!")
            sentry_sdk.capture_exception(e)



print("Clearing todos")
clear_todos()
print("Done")
