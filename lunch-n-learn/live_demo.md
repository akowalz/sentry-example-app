# Intro

Ok, now that we've gotten familiar with Sentry's UI and basic concepts, let's look at how to
integrate Sentry into a real application.

Here I've got a simple web todo-list web app.  You can log in as a user, and add todos.
Unfortunately the app has a pretty big bug, if you add a todo but don't specify a due date, 
the app crashes.

_start app in production mode, do the demo that brings you to the 500 page_

Being a developer with no sense of user behavior, I never would have expecteed users to omit
the due date a on a todo, and so I have no idea this bug exists.  If this app were deployed in production
how would I know that users were encountering this error?

This is where Sentry comes in. Let's integrate Sentry into this app so we can figure out what's happening.

# Install and Setup

The first thing we need to do is install the Sentrty SDK, I'm using Pipenv so I can do this easily
but adding the SDK to my Pipfile:

```
# Pipfile

[packages]
flask = "*"
flask_sqlalchemy = "*"
sentry-sdk = "*"
# "sentry-sdk[flask]" = "*"
```

and install.

Ok, I've got Sentry added, but I'm not ready yet.  I also need a Sentry project to send these
exceptions too.  Luckily, I've already created one.  The project settings page gives me the code
I need to get started.

_navigate to https://sentry.io/settings/alex-kowalczuk/projects/sentry-example-app/install/python/_

The snippet comes preloaded with our project ID (technically our DSN). Let's add this snippet to the app:

```python
# app.py

import sentry_sdk
sentry_sdk.init("https://40c3c5d83e5a46199f063c0ac2b5d200@sentry.io/1390866")
```

Cool, although, in this case, that's not quite enough to start tracking exceptions.  We also need to
hook into our application's error handler to start tracking the exceptions.

```python
@app.errorhandler(Exception)
def handle_exception(e):
    sentry_sdk.capture_exception(e)
    raise e
```

Now, any time an exception is caught during an HTTP request, it will be captured and automatically sent to Sentry.  Let's give it a shot.

## Flask Setup

It turns out that Sentry provides integrations into a lot of frameworks so we can skip this step. Instead of manually capturing the exceptions, we can instead use the flask SDK integration.

```python
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://40c3c5d83e5a46199f063c0ac2b5d200@sentry.io/1390866",
    integrations=[FlaskIntegration()],
)

# delete the error handler
```

Generally, it's best to use the integrations that are provided for us, but I think it's helpful to have some idea what they're doing behind the scenes - just catching exceptions and sending them to Sentry.

# User Context

Sentry also allows us to set custom context on events.  Generally, the most important type of context to 
set is user context.  Users are streated as special snowflakes in Sentry, and user context let's us do cool
things like only a send alerts after an issue effects a certain number of users, and get metrics on impact.

Let's add some user context to our Sentry exceptions.  We need to do this at a point in the request lifecycle
when using information is available.  In our app, user info is stored in the session and should be available at the top of every request.  Flask allows us to add actions before requests, which is the perfect time to add this context:


```python
@app.before_request
def setup_setry_context():
    with sentry_sdk.configure_scope() as scope:
        if 'user' in session:
            scope.user = {"id" : session['user']}
```

You can add as much user data as you like, but the "id" key is special.  This is the key that Sentry will use to primarly identify users and group their exceptions.  At ActiveCampaign, it's probably best to store the account name as the ID, and user information like email as additional user context.  This will allow us to figure out how many accounts an issue affects.

Let's check out our new user context with a few users.

# Further configuration


Sentry will group exceptions for you by environment.  Usually, it's a bad idea to send exceptions in the dev environment like I'm doing here, so be sure not to do that.

## Configure Environment

```python
sentry_sdk.init(
    dsn="https://40c3c5d83e5a46199f063c0ac2b5d200@sentry.io/1390866",
    environment=app.config["ENV"],
    integrations=[FlaskIntegration()],
)
```

Now, we'll be able to distinguish staging and production exceptions, for example.

If you don't want to send an event in a particular environment, you can use the a before action do so.

```
def before_sentry_send(event, hint):
    if app.config["ENV"] == "development":
        return None

    return event

sentry_sdk.init(
    dsn="https://40c3c5d83e5a46199f063c0ac2b5d200@sentry.io/1390866",
    environment=app.config["ENV"],
    integrations=[FlaskIntegration()],
    before_send=before_sentry_send
)
```

You could also just not configure the SDK, it's up to you what to do here.

## Ignore Exceptions

You can also ignore certain classes of exceptions.  For example, Flask will raise a NotFound error if someone visits a URL that doesn't exist. This doesn't seem like a very good use of our Sentry bandwidth.  Let's ignore this class of exception entirely.



```python
import werkzeug.exceptions

# ignore_errors=[werkzeug.exceptions.NotFound],
```

# Capture Exceptions outside of HTTP Requests

So, the Flask Sentry SDK shows us how to capture exceptions during HTTP requests, but sometimes we want to some
more custom exception catching.  For example, my app has a cron job that clears completed tasks at the end of every day.  What if we want to capture exceptions during this?

The good news is that the Sentry Flask SDK is smart enough to hook itself into wherever your Flask app is initialized.  I consider this magic, so be careful with it.  If you have background or cron jobs, _always_ confirm they are properly reporting their errors.

So, our cron job has a pretty obvious bug.  Unfortunately, when this bug happens, it kills the whole job and we can't continue.  We want to know what bugs are occurring in Sentry, but we also want to keep the process moving.  Let's look at how we can do that.


```python
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
      capture_exception(e)
```

Now, when we run this, we'll capture the exception in Sentry without totally killing the job.

## Adding custom tags and context

This is also a good example of when to use tags and context.  Let's say we want to make it easy to quickly find all of the exceptions that are happening within our various cron jobs.  We can use a Sentry tag to index our events and issues and make it easy to search for them.

```
with sentry_sdk.configure_scope() as scope:
    scope.set_tag("cron-job", "clear_todos")
```

If a user was complaining their todos weren't getting deleted at the end of the day, you could search for that user and/or this job, and quickly figure out if an exception was causing the problem.

We can also add more unstructured data in the form of extra context.  In this case, it might make sense to add some information about the problematic todo.


```
with sentry_sdk.configure_scope() as scope:
    scope.set_tag("cron-job", "clear_todos")
    scope.set_extra("todo.id", todo.id)
    scope.set_extra("todo.text", todo.text)
    sentry_sdk.capture_exception(e)
```

Now, if a particular todo blows up this job, we can quickly figure out what about cause this to happen.

A good example using extra context might be a webhook processor, where your extra context could be the webhook payload.
